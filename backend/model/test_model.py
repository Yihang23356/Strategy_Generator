import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm_model import Evaluator_openai_llm, actor_openai_llm


def run_test(name, llm):
    print(f"=== Testing {name} ===")
    try:
        response = llm.invoke("请只回复: ok")
        content = getattr(response, "content", response)
        print(f"{name} success")
        print(f"{name} response: {content}")
        return True
    except Exception as exc:
        print(f"{name} failed: {type(exc).__name__}: {exc}")
        return False


def main():
    actor_ok = run_test("actor_openai_llm", actor_openai_llm)
    evaluator_ok = run_test("Evaluator_openai_llm", Evaluator_openai_llm)

    if actor_ok and evaluator_ok:
        print("All model tests passed.")
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
