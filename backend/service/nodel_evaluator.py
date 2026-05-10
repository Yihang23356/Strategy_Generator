import difflib
import json
from typing import Dict, List, Optional, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated

from model.llm_model import Evaluator_openai_llm
from utils import add_event, get_logger, load_prompt, project_relative, resolve_project_path


logger = get_logger(__name__)
OUTPUT_PARSER = StrOutputParser()


@tool
def list_files(relative_dir: str = ".", max_entries: int = 200) -> str:
    """List project files."""
    add_event("evaluator", f"工具调用：list_files({relative_dir})", event_type="tool")
    base = resolve_project_path(relative_dir)
    entries: List[str] = []
    for i, path in enumerate(sorted(base.iterdir(), key=lambda item: item.name.lower())):
        if i >= max_entries:
            break
        kind = "DIR" if path.is_dir() else "FILE"
        entries.append(f"[{kind}] {project_relative(path)}")
    return "\n".join(entries)


@tool
def read_file(relative_path: str, start_line: int = 1, end_line: int = 300) -> str:
    """Read a project file with line numbers."""
    add_event(
        "evaluator",
        f"工具调用：read_file({relative_path})",
        event_type="tool",
        data={"start_line": start_line, "end_line": end_line},
    )
    target = resolve_project_path(relative_path)
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    start_line = max(start_line, 1)
    end_line = min(max(end_line, start_line), len(lines))
    width = len(str(end_line))
    return "\n".join(
        f"{str(index).rjust(width)}| {lines[index - 1]}"
        for index in range(start_line, end_line + 1)
    )


@tool
def compare_files(file_a: str, file_b: str, context_lines: int = 3) -> str:
    """Compare two project files."""
    add_event(
        "evaluator",
        f"工具调用：compare_files({file_a}, {file_b})",
        event_type="tool",
        data={"context_lines": context_lines},
    )
    path_a = resolve_project_path(file_a)
    path_b = resolve_project_path(file_b)
    diff = difflib.unified_diff(
        path_a.read_text(encoding="utf-8", errors="replace").splitlines(),
        path_b.read_text(encoding="utf-8", errors="replace").splitlines(),
        fromfile=file_a,
        tofile=file_b,
        lineterm="",
        n=max(context_lines, 0),
    )
    return "\n".join(diff)


TOOLS = [list_files, read_file, compare_files]
tool_node = ToolNode(TOOLS)
evaluator_with_tools = Evaluator_openai_llm.bind_tools(TOOLS)


class EvaluatorState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    round_count: int
    max_rounds: int


def evaluator_node(state: EvaluatorState) -> EvaluatorState:
    add_event("evaluator", "调用评价者大模型", event_type="llm")
    response = evaluator_with_tools.invoke(state["messages"])
    tool_calls = getattr(response, "tool_calls", None) or []
    if tool_calls:
        add_event(
            "evaluator",
            "评价者大模型请求调用工具",
            event_type="tool_request",
            data={"tools": [call.get("name", "") for call in tool_calls]},
        )
    return {
        "messages": [response],
        "round_count": state.get("round_count", 0) + 1,
    }


def route_after_evaluator(state: EvaluatorState) -> str:
    has_tool_calls = bool(getattr(state["messages"][-1], "tool_calls", None))
    if not has_tool_calls:
        return END
    if state.get("round_count", 0) >= state.get("max_rounds", 8):
        add_event("evaluator", "评价工具轮数已达上限，强制收敛最终评价", event_type="warning")
        return END
    return "tools"


builder = StateGraph(EvaluatorState)
builder.add_node("evaluator", evaluator_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "evaluator")
builder.add_conditional_edges(
    "evaluator",
    route_after_evaluator,
    {"tools": "tools", END: END},
)
builder.add_edge("tools", "evaluator")
evaluator_graph = builder.compile()


def run_evaluator_review(
    review_request: str,
    target_files: Optional[List[str]] = None,
    max_rounds: int = 8,
) -> Dict[str, str]:
    add_event("evaluator", "评价任务开始", data={"target_files": target_files or []})
    file_hint = ""
    if target_files:
        file_hint = "优先读取这些文件：\n" + "\n".join(f"- {path}" for path in target_files)

    init_state: EvaluatorState = {
        "messages": [
            SystemMessage(content=load_prompt("evaluator_prompt.json", "system")),
            HumanMessage(content=f"{review_request}\n\n{file_hint}"),
        ],
        "round_count": 0,
        "max_rounds": max_rounds,
    }
    result = evaluator_graph.invoke(init_state)
    last_message = result["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        add_event("evaluator", "停止继续调用工具，改为直接输出最终评价", event_type="llm")
        forced_answer = Evaluator_openai_llm.invoke(
            result["messages"]
            + [HumanMessage(content=load_prompt("evaluator_prompt.json", "force_final"))]
        )
        final_raw = (
            forced_answer.content
            if isinstance(forced_answer.content, str)
            else str(forced_answer.content)
        )
    else:
        final_raw = last_message.content if isinstance(last_message.content, str) else str(last_message.content)
    add_event("evaluator", "评价任务结束", data={"rounds": result.get("round_count", 0)})
    return {
        "final_review": OUTPUT_PARSER.invoke(final_raw),
        "rounds": str(result.get("round_count", 0)),
    }


def review_file_pair(
    file_a: str,
    file_b: str,
    extra_requirements: str = "",
    max_rounds: int = 8,
) -> Dict[str, str]:
    request = (
        f"请对比 `{file_a}` 与 `{file_b}`，先找差异，再做代码评审。"
        f"\n额外要求：{extra_requirements}"
    )
    return run_evaluator_review(
        review_request=request,
        target_files=[file_a, file_b],
        max_rounds=max_rounds,
    )


def review_to_markdown(result: Dict[str, str]) -> str:
    return (
        "## 评审输出\n"
        f"- 轮数: {result['rounds']}\n"
        "- 评审结论:\n\n"
        f"{result['final_review']}"
    )


if __name__ == "__main__":
    demo = review_file_pair(
        file_a="service/graph.py",
        file_b="model/llm_model.py",
        extra_requirements="重点关注可维护性、健壮性与安全性。",
    )
    print(json.dumps(demo, ensure_ascii=False, indent=2))
