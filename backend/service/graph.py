import json
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from .nodel_actor import run_actor_task
from .nodel_evaluator import run_evaluator_review
from .nodel_plan_formulation import plan_formulation_node
from utils import add_event, get_logger, load_prompt, normalize_input_file, normalize_input_files, set_current_run


OUTPUT_PARSER = StrOutputParser()
logger = get_logger(__name__)


class GateResult(BaseModel):
    passed: bool = Field(description="Whether the review passes.")
    score: int = Field(ge=0, le=100, description="Review score from 0 to 100.")
    reason: str = Field(description="Short reason for the score.")
    feedback: str = Field(description="Concrete feedback for the next iteration.")


GATE_PARSER = PydanticOutputParser(pydantic_object=GateResult)


class GraphState(TypedDict):
    audit_task: str
    quality_bar: str
    pass_score: int
    max_iterations: int
    input_files: List[str]
    standard_file: str
    iteration: int
    current_plan: str
    actor_output: str
    actor_result_file: str
    evaluator_output: str
    passed: bool
    history: List[Dict[str, Any]]


def _format_file_list(paths: List[str]) -> str:
    return "\n".join(f"- {path}" for path in paths)


def _build_actor_task(state: GraphState, result_file: str) -> str:
    return load_prompt("actor_prompt.json", "graph_task").format(
        audit_task=state["audit_task"],
        input_files=_format_file_list(state["input_files"]),
        standard_file=state["standard_file"],
        result_file=result_file,
        current_plan=state["current_plan"],
    )


def actor_node(state: GraphState) -> GraphState:
    iteration = state["iteration"] + 1
    result_file = f"output/review_round_{iteration}/result.json"
    add_event("actor", f"进入执行节点，第 {iteration} 轮", data={"result_file": result_file})
    actor_result = run_actor_task(
        task=_build_actor_task(state, result_file),
        result_file=result_file,
    )
    actor_output = json.dumps(actor_result, ensure_ascii=False)
    history = list(state.get("history", []))
    history.append(
        {
            "round": iteration,
            "plan": state["current_plan"],
            "actor_result": actor_result,
            "actor_result_file": actor_result["result_file"],
        }
    )
    logger.info(
        "graph.actor_node completed: iteration=%s, result_file=%s",
        iteration,
        actor_result["result_file"],
    )
    add_event(
        "actor",
        "执行节点完成",
        data={
            "result_file": actor_result["result_file"],
            "tools": actor_result.get("tool_events", []),
        },
    )
    return {
        "iteration": iteration,
        "actor_output": actor_output,
        "actor_result_file": actor_result["result_file"],
        "history": history,
    }


def _build_evaluator_prompt(state: GraphState) -> str:
    return load_prompt("evaluator_prompt.json", "user").format(
        quality_bar=state["quality_bar"],
        pass_score=state["pass_score"],
        input_files=_format_file_list(state["input_files"]),
        standard_file=state["standard_file"],
        result_file=state["actor_result_file"],
        format_instructions=GATE_PARSER.get_format_instructions(),
    )


def evaluator_node(state: GraphState) -> GraphState:
    add_event(
        "evaluator",
        "进入评价节点",
        data={"target_files": [state["actor_result_file"], state["standard_file"], *state["input_files"]]},
    )
    result = run_evaluator_review(
        review_request=_build_evaluator_prompt(state),
        target_files=[state["actor_result_file"], state["standard_file"], *state["input_files"]],
        max_rounds=12,
    )
    evaluator_output = OUTPUT_PARSER.invoke(result["final_review"])
    gate = GATE_PARSER.parse(evaluator_output)
    passed = gate.passed and gate.score >= state["pass_score"]

    history = list(state.get("history", []))
    if history:
        history[-1]["evaluator_feedback"] = evaluator_output
        history[-1]["gate"] = {
            **gate.model_dump(),
            "pass_score": state["pass_score"],
            "passed_with_threshold": passed,
        }
    logger.info(
        "graph.evaluator_node completed: iteration=%s, score=%s, passed=%s",
        state["iteration"],
        gate.score,
        passed,
    )
    add_event(
        "evaluator",
        "评价节点完成",
        data={"score": gate.score, "passed": passed, "reason": gate.reason},
    )
    return {
        "evaluator_output": evaluator_output,
        "passed": passed,
        "history": history,
    }


def route_after_evaluator(state: GraphState) -> str:
    if state["passed"]:
        add_event("router", "评分已达标，流程结束")
        return END
    if state["iteration"] >= state["max_iterations"]:
        add_event("router", "达到最大迭代次数，流程结束")
        return END
    add_event("router", "评分未达标，回到方案制定节点继续迭代")
    return "plan_formulation"


builder = StateGraph(GraphState)
builder.add_node("plan_formulation", plan_formulation_node)
builder.add_node("actor", actor_node)
builder.add_node("evaluator", evaluator_node)
builder.add_edge(START, "plan_formulation")
builder.add_edge("plan_formulation", "actor")
builder.add_edge("actor", "evaluator")
builder.add_conditional_edges(
    "evaluator",
    route_after_evaluator,
    {"plan_formulation": "plan_formulation", END: END},
)
actor_evaluator_graph = builder.compile()


def run_dynamic_review_graph(
    input_files: List[str],
    standard_file: str,
    audit_task: str = "请完成动态审核并输出结构化结果",
    quality_bar: str = "结果准确、可解释、可复现",
    pass_score: int = 90,
    max_iterations: int = 3,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    set_current_run(run_id)
    add_event("graph", "审核图开始运行", data={"max_iterations": max_iterations, "pass_score": pass_score})
    if len(input_files) != 3:
        raise ValueError("input_files must contain exactly 3 files")
    if not 0 <= pass_score <= 100:
        raise ValueError("pass_score must be between 0 and 100")
    if max_iterations < 1:
        raise ValueError("max_iterations must be greater than 0")

    normalized_input_files = normalize_input_files(input_files)
    normalized_standard_file = normalize_input_file(standard_file)
    add_event(
        "graph",
        "输入文件归一化完成",
        data={"input_files": normalized_input_files, "standard_file": normalized_standard_file},
    )

    init_state: GraphState = {
        "audit_task": audit_task,
        "quality_bar": quality_bar,
        "pass_score": pass_score,
        "max_iterations": max_iterations,
        "input_files": normalized_input_files,
        "standard_file": normalized_standard_file,
        "iteration": 0,
        "current_plan": "",
        "actor_output": "",
        "actor_result_file": "",
        "evaluator_output": "",
        "passed": False,
        "history": [],
    }
    state = actor_evaluator_graph.invoke(init_state)
    add_event("graph", "审核图运行完成", data={"passed": state["passed"], "iterations": state["iteration"]})
    return {
        "audit_task": state["audit_task"],
        "input_files": state["input_files"],
        "standard_file": state["standard_file"],
        "pass_score": state["pass_score"],
        "passed": state["passed"],
        "iterations": state["iteration"],
        "final_plan": state["current_plan"],
        "final_actor_result_file": state["actor_result_file"],
        "final_audit_result": state["actor_output"],
        "final_review": state["evaluator_output"],
        "history": state["history"],
    }


def graph_mermaid() -> str:
    return (
        "flowchart TD\n"
        "  START([start]) --> PLAN[nodel_plan_formulation]\n"
        "  PLAN --> ACTOR[nodel_actor]\n"
        "  ACTOR --> RESULT[result.json]\n"
        "  RESULT --> EVAL[nodel_evaluator]\n"
        "  EVAL -->|passed| END([output])\n"
        "  EVAL -->|failed| PLAN\n"
    )


if __name__ == "__main__":
    demo = run_dynamic_review_graph(
        input_files=["input_a.json", "input_b.json", "input_c.json"],
        standard_file="standard_answer.json",
        audit_task="根据三份输入差异完成审核并输出结果",
        quality_bar="审核结果正确、覆盖关键差异、说明清晰",
        pass_score=90,
        max_iterations=3,
    )
    print(json.dumps(demo, ensure_ascii=False, indent=2))
