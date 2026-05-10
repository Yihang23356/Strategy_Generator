import json
from functools import lru_cache
from typing import Any, Dict

from .paths import PROMPT_ROOT


@lru_cache(maxsize=None)
def load_prompt_file(file_name: str) -> Dict[str, Any]:
    path = PROMPT_ROOT / file_name
    return json.loads(path.read_text(encoding="utf-8"))


def load_prompt(file_name: str, key: str) -> str:
    value = load_prompt_file(file_name)[key]
    if not isinstance(value, str):
        raise TypeError(f"prompt {file_name}:{key} must be a string")
    return value
