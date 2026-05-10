from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from model.llm_model import actor_openai_llm
from utils import add_event, get_logger, load_prompt


OUTPUT_PARSER = StrOutputParser()
logger = get_logger(__name__)


def _format_file_list(paths: List[str]) -> str:
    return "\n".join(f"- {path}" for path in paths)


def _build_plan_prompt(state: Dict[str, Any]) -> List[SystemMessage | HumanMessage]:
    feedback = ""
    history = state.get("history") or []
    if history:
        feedback = f"\n上一轮评价者反馈：\n{history[-1].get('evaluator_feedback', '')}\n"

    return [
        SystemMessage(content=load_prompt("plan_prompt.json", "system")),
        HumanMessage(
            content=load_prompt("plan_prompt.json", "user").format(
                audit_task=state["audit_task"],
                input_files=_format_file_list(state["input_files"]),
                standard_file=state["standard_file"],
                quality_bar=state["quality_bar"],
                feedback=feedback,
            )
        ),
    ]


def plan_formulation_node(state: Dict[str, Any]) -> Dict[str, str]:
    add_event("plan_formulation", "进入方案制定节点")
    add_event("plan_formulation", "调用大模型生成执行方案", event_type="llm")
    response = actor_openai_llm.invoke(_build_plan_prompt(state))
    raw_plan = response.content if isinstance(response.content, str) else str(response.content)
    plan_text = OUTPUT_PARSER.invoke(raw_plan)
    logger.info("plan_formulation_node done, plan_len=%s", len(plan_text))
    add_event("plan_formulation", "方案制定完成", data={"plan_length": len(plan_text)})
    return {"current_plan": plan_text}
