from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from model.llm_model import actor_openai_llm
from utils import (
    PROJECT_ROOT,
    WORKSPACE_ROOT,
    add_event,
    get_logger,
    load_prompt,
    project_relative,
    resolve_workspace_path,
)


logger = get_logger(__name__)
ACTOR_HISTORY_LOG = PROJECT_ROOT / "log" / "actor_run_history.jsonl"
RECENT_TOOL_EVENTS: List[str] = []


class ActorResult(BaseModel):
    status: str = Field(description="Execution status, such as success or failed.")
    changed_files: List[str] = Field(description="Project-relative files changed by actor.")
    commands: List[str] = Field(description="Commands or snippets executed by actor.")
    summary: str = Field(description="Short execution summary.")


ACTOR_RESULT_PARSER = PydanticOutputParser(pydantic_object=ActorResult)
actor_result_llm = actor_openai_llm.with_structured_output(ActorResult)


def _record_tool_event(event: str) -> None:
    RECENT_TOOL_EVENTS.append(event)
    add_event("actor", f"工具调用：{event}", event_type="tool", data={"tool_event": event})


def _read_recent_history(max_records: int = 5) -> str:
    if not ACTOR_HISTORY_LOG.exists():
        return ""
    lines = ACTOR_HISTORY_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    items: List[str] = []
    for raw in lines[-max_records:]:
        data = json.loads(raw)
        items.append(
            f"- time={data.get('time', '')}; "
            f"task={str(data.get('task', ''))[:120]}; "
            f"result={str(data.get('result_preview', ''))[:120]}"
        )
    return "\n".join(items)


def _append_run_history(task: str, result: Dict[str, Any]) -> None:
    ACTOR_HISTORY_LOG.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "task": task,
        "result_preview": json.dumps(result, ensure_ascii=False)[:500],
        "tool_events": RECENT_TOOL_EVENTS,
    }
    with ACTOR_HISTORY_LOG.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")


@tool
def create_workspace_directory(relative_dir: str) -> str:
    """Create a directory under workspace."""
    target = resolve_workspace_path(relative_dir)
    target.mkdir(parents=True, exist_ok=True)
    rel = project_relative(target)
    _record_tool_event(f"mkdir:{rel}")
    return rel


@tool
def write_code_file(relative_path: str, content: str) -> str:
    """Write one file under workspace."""
    target = resolve_workspace_path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    rel = project_relative(target)
    _record_tool_event(f"write:{rel}")
    return rel


@tool
def append_code_file(relative_path: str, content: str) -> str:
    """Append one code chunk to a file under workspace."""
    target = resolve_workspace_path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="") as fp:
        fp.write(content)
    rel = project_relative(target)
    _record_tool_event(f"append:{rel}:{len(content)}")
    return rel


@tool
def write_code_file_chunks(relative_path: str, chunks_json: str) -> str:
    """Write one file under workspace from a JSON list of string chunks."""
    chunks = json.loads(chunks_json)
    target = resolve_workspace_path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(str(chunk) for chunk in chunks), encoding="utf-8")
    rel = project_relative(target)
    _record_tool_event(f"write_chunks:{rel}:{len(chunks)}")
    return rel


@tool
def write_multiple_code_files(files_json: str) -> str:
    """Write multiple files under workspace from JSON list."""
    items = json.loads(files_json)
    if not isinstance(items, list):
        return "tool_error: files_json must be a JSON list."

    written: List[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return f"tool_error: item {index} must be an object with relative_path and content."
        if "relative_path" not in item:
            return f"tool_error: item {index} is missing required field relative_path."
        if "content" not in item:
            return f"tool_error: item {index} is missing required field content."

        target = resolve_workspace_path(str(item["relative_path"]))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(item["content"]), encoding="utf-8")
        written.append(project_relative(target))
    _record_tool_event(f"write_multiple:{len(written)}")
    return "\n".join(written)


@tool
def read_code_file(relative_path: str) -> str:
    """Read one file under workspace."""
    target = resolve_workspace_path(relative_path)
    _record_tool_event(f"read:{project_relative(target)}")
    return target.read_text(encoding="utf-8")


@tool
def read_code_file_lines(relative_path: str, start_line: int = 1, end_line: int = 200) -> str:
    """Read selected lines from one file under workspace."""
    target = resolve_workspace_path(relative_path)
    lines = target.read_text(encoding="utf-8").splitlines()
    start_line = max(start_line, 1)
    end_line = min(max(end_line, start_line), len(lines))
    width = len(str(end_line))
    _record_tool_event(f"read_lines:{project_relative(target)}:{start_line}-{end_line}")
    return "\n".join(
        f"{str(index).rjust(width)}| {lines[index - 1]}"
        for index in range(start_line, end_line + 1)
    )


@tool
def replace_in_code_file(relative_path: str, old_text: str, new_text: str, count: int = 0) -> str:
    """Replace text in one workspace file."""
    target = resolve_workspace_path(relative_path)
    text = target.read_text(encoding="utf-8")
    replaced = text.replace(old_text, new_text, count if count > 0 else -1)
    target.write_text(replaced, encoding="utf-8")
    rel = project_relative(target)
    _record_tool_event(f"replace:{rel}")
    return rel


@tool
def list_workspace_files(relative_dir: str = ".", max_entries: int = 300) -> str:
    """List files under workspace."""
    base = resolve_workspace_path(relative_dir)
    entries: List[str] = []
    for i, path in enumerate(sorted(base.rglob("*"))):
        if i >= max_entries:
            break
        kind = "DIR" if path.is_dir() else "FILE"
        entries.append(f"[{kind}] {path.relative_to(WORKSPACE_ROOT).as_posix()}")
    _record_tool_event(f"list:{relative_dir}")
    return "\n".join(entries)


@tool
def run_python_file(relative_path: str, timeout_seconds: int = 20) -> str:
    """Run a Python file under workspace."""
    target = resolve_workspace_path(relative_path)
    result = subprocess.run(
        [sys.executable, str(target)],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        cwd=str(WORKSPACE_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    _record_tool_event(f"run_file:{project_relative(target)}:exit={result.returncode}")
    return f"exit_code={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"


@tool
def run_python_file_with_args(relative_path: str, args_json: str = "[]", timeout_seconds: int = 30) -> str:
    """Run a Python file under workspace with JSON args."""
    target = resolve_workspace_path(relative_path)
    args = [str(arg) for arg in json.loads(args_json)]
    result = subprocess.run(
        [sys.executable, str(target), *args],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        cwd=str(WORKSPACE_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    _record_tool_event(f"run_file_args:{project_relative(target)}:exit={result.returncode}")
    return f"exit_code={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"


@tool
def run_python_snippet(code: str, timeout_seconds: int = 20) -> str:
    """Run a temporary Python snippet under workspace."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        encoding="utf-8",
        delete=False,
        dir=WORKSPACE_ROOT,
    ) as fp:
        fp.write(code)
        temp_path = Path(fp.name)
    try:
        result = subprocess.run(
            [sys.executable, str(temp_path)],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=str(WORKSPACE_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        _record_tool_event(f"run_snippet:{temp_path.name}:exit={result.returncode}")
        return f"exit_code={result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    finally:
        temp_path.unlink(missing_ok=True)


@tool
def read_actor_history(max_records: int = 10) -> str:
    """Read recent actor run history."""
    return _read_recent_history(max_records=max_records)


TOOLS = [
    create_workspace_directory,
    write_code_file,
    append_code_file,
    write_code_file_chunks,
    write_multiple_code_files,
    read_code_file,
    read_code_file_lines,
    replace_in_code_file,
    list_workspace_files,
    run_python_file,
    run_python_file_with_args,
    run_python_snippet,
    read_actor_history,
]
tool_node = ToolNode(TOOLS)
actor_with_tools = actor_openai_llm.bind_tools(TOOLS)


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


def actor_node(state: AgentState) -> AgentState:
    add_event("actor", "调用执行者大模型", event_type="llm")
    response = actor_with_tools.invoke(state["messages"])
    tool_calls = getattr(response, "tool_calls", None) or []
    if tool_calls:
        add_event(
            "actor",
            "执行者大模型请求调用工具",
            event_type="tool_request",
            data={"tools": [call.get("name", "") for call in tool_calls]},
        )
    return {"messages": [response]}


def route_after_actor(state: AgentState) -> str:
    return "tools" if getattr(state["messages"][-1], "tool_calls", None) else END


builder = StateGraph(AgentState)
builder.add_node("actor", actor_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "actor")
builder.add_conditional_edges("actor", route_after_actor, {"tools": "tools", END: END})
builder.add_edge("tools", "actor")
actor_service_graph = builder.compile()


def run_actor_task(
    task: str,
    result_file: str = "output/result.json",
    recursion_limit: int = 100,
) -> Dict[str, Any]:
    RECENT_TOOL_EVENTS.clear()
    add_event("actor", "执行者任务开始", data={"result_file": result_file})
    result_path = resolve_workspace_path(result_file)
    history_text = _read_recent_history(max_records=5)

    messages: List[AnyMessage] = [
        SystemMessage(content=load_prompt("actor_prompt.json", "system")),
    ]
    if history_text:
        messages.append(
            SystemMessage(
                content=load_prompt("actor_prompt.json", "history").format(history=history_text)
            )
        )
    messages.append(
        HumanMessage(
            content=load_prompt("actor_prompt.json", "user").format(
                task=task,
                format_instructions=ACTOR_RESULT_PARSER.get_format_instructions(),
            )
        )
    )

    result = actor_service_graph.invoke(
        {"messages": messages},
        config={"recursion_limit": recursion_limit},
    )
    final_raw = result["messages"][-1].content
    add_event("actor", "整理执行者结构化结果", event_type="llm")
    structured = actor_result_llm.invoke(
        [
            SystemMessage(
                content=(
                    "根据执行者对话和工具调用事实，输出 ActorResult。"
                    "只汇总已经实际创建、修改、读取或运行过的内容，不编造。"
                )
            ),
            HumanMessage(
                content=(
                    f"执行者最终回复：\n{final_raw}\n\n"
                    f"工具事件：\n{json.dumps(RECENT_TOOL_EVENTS, ensure_ascii=False, indent=2)}\n\n"
                    "请输出 status、changed_files、commands、summary。"
                )
            ),
        ]
    )
    actor_result = structured.model_dump() if hasattr(structured, "model_dump") else dict(structured)
    actor_result["result_file"] = project_relative(result_path)
    actor_result["tool_events"] = list(RECENT_TOOL_EVENTS)

    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(actor_result, ensure_ascii=False, indent=2), encoding="utf-8")
    _append_run_history(task=task, result=actor_result)
    logger.info("run_actor_task done, result_file=%s", actor_result["result_file"])
    add_event(
        "actor",
        "执行者任务结束",
        data={
            "status": actor_result["status"],
            "changed_files": actor_result["changed_files"],
            "commands": actor_result["commands"],
        },
    )
    return actor_result


if __name__ == "__main__":
    print(json.dumps(run_actor_task("Create hello.py and run it."), ensure_ascii=False, indent=2))
