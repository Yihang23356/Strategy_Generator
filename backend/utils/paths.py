from pathlib import Path
from typing import Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = (PROJECT_ROOT / "workspace").resolve()
INPUT_ROOT = (WORKSPACE_ROOT / "input").resolve()
PROMPT_ROOT = (PROJECT_ROOT / "prompt").resolve()

WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
INPUT_ROOT.mkdir(parents=True, exist_ok=True)


def _ensure_inside(root: Path, target: Path) -> Path:
    target = target.resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"path out of scope: {target}")
    return target


def project_relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def resolve_project_path(path_text: str) -> Path:
    if not path_text or not path_text.strip():
        raise ValueError("path is empty")
    raw = Path(path_text)
    target = raw.resolve() if raw.is_absolute() else (PROJECT_ROOT / raw).resolve()
    return _ensure_inside(PROJECT_ROOT, target)


def resolve_workspace_path(path_text: str) -> Path:
    if not path_text or not path_text.strip():
        raise ValueError("path is empty")
    raw = Path(path_text)
    target = raw.resolve() if raw.is_absolute() else (WORKSPACE_ROOT / raw).resolve()
    return _ensure_inside(WORKSPACE_ROOT, target)


def normalize_input_file(path_text: str) -> str:
    if not path_text or not path_text.strip():
        raise ValueError("input file path is empty")
    raw = Path(path_text)
    if raw.is_absolute():
        target = raw.resolve()
    elif raw.as_posix().startswith("workspace/input/"):
        target = (PROJECT_ROOT / raw).resolve()
    else:
        target = (INPUT_ROOT / raw).resolve()
    target = _ensure_inside(INPUT_ROOT, target)
    if not target.is_file():
        raise FileNotFoundError(f"input file not found: {target}")
    return project_relative(target)


def normalize_input_files(paths: Iterable[str]) -> List[str]:
    return [normalize_input_file(path) for path in paths]
