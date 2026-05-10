from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from openai import APIConnectionError, OpenAIError
from pydantic import BaseModel, Field

from utils import INPUT_ROOT, add_event, create_run, get_run, project_relative, set_error, set_result


router = APIRouter(prefix="/api/review", tags=["review"])


class ReviewRunRequest(BaseModel):
    input_files: List[str] = Field(min_length=3, max_length=3)
    standard_file: str
    audit_task: str = "请完成动态审核并输出结构化结果"
    quality_bar: str = "结果准确、可解释、可复现"
    pass_score: int = Field(default=90, ge=0, le=100)
    max_iterations: int = Field(default=3, ge=1)


class FileContent(BaseModel):
    path: str
    content: str


class ReviewRunWithContentRequest(BaseModel):
    input_files: List[FileContent] = Field(min_length=3, max_length=3)
    standard_file: FileContent
    audit_task: str = "请完成动态审核并输出结构化结果"
    quality_bar: str = "结果准确、可解释、可复现"
    pass_score: int = Field(default=90, ge=0, le=100)
    max_iterations: int = Field(default=3, ge=1)


def _write_input_file(file_data: FileContent) -> str:
    raw = Path(file_data.path)
    if raw.is_absolute():
        raise ValueError("file path must be relative")
    target = (INPUT_ROOT / raw).resolve()
    if target != INPUT_ROOT and INPUT_ROOT not in target.parents:
        raise ValueError(f"path out of scope: {file_data.path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(file_data.content, encoding="utf-8")
    return project_relative(target)


async def _write_upload_file(file: UploadFile, role: str) -> str:
    filename = Path(file.filename or "").name
    if not filename:
        raise ValueError(f"{role} file name is empty")
    target = (INPUT_ROOT / "uploads" / f"{role}_{filename}").resolve()
    if target != INPUT_ROOT and INPUT_ROOT not in target.parents:
        raise ValueError(f"path out of scope: {filename}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(await file.read())
    return project_relative(target)


def _run_review_job(
    run_id: str,
    input_files: List[str],
    standard_file: str,
    audit_task: str,
    quality_bar: str,
    pass_score: int,
    max_iterations: int,
) -> None:
    try:
        from service.graph import run_dynamic_review_graph

        add_event("route", "后台审核任务开始", run_id=run_id)
        result = run_dynamic_review_graph(
            input_files=input_files,
            standard_file=standard_file,
            audit_task=audit_task,
            quality_bar=quality_bar,
            pass_score=pass_score,
            max_iterations=max_iterations,
            run_id=run_id,
        )
        set_result(run_id, result)
    except Exception as exc:
        add_event("route", "后台审核任务失败", event_type="error", data={"error": str(exc)}, run_id=run_id)
        set_error(run_id, str(exc))


@router.get("/graph")
def get_review_graph() -> Dict[str, str]:
    try:
        from service.graph import graph_mermaid

        return {"mermaid": graph_mermaid()}
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"missing backend dependency: {exc.name}") from exc


@router.get("/runs/{run_id}")
def get_review_run(run_id: str) -> Dict[str, Any]:
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@router.post("/run")
async def run_review(request: ReviewRunRequest) -> Dict[str, Any]:
    try:
        from service.graph import run_dynamic_review_graph

        return await run_in_threadpool(
            run_dynamic_review_graph,
            input_files=request.input_files,
            standard_file=request.standard_file,
            audit_task=request.audit_task,
            quality_bar=request.quality_bar,
            pass_score=request.pass_score,
            max_iterations=request.max_iterations,
        )
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"missing backend dependency: {exc.name}") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail=f"llm api connection failed: {exc}") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"llm api error: {exc}") from exc
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/run-with-content")
async def run_review_with_content(request: ReviewRunWithContentRequest) -> Dict[str, Any]:
    try:
        from service.graph import run_dynamic_review_graph

        input_files = [_write_input_file(file_data) for file_data in request.input_files]
        standard_file = _write_input_file(request.standard_file)
        return await run_in_threadpool(
            run_dynamic_review_graph,
            input_files=input_files,
            standard_file=standard_file,
            audit_task=request.audit_task,
            quality_bar=request.quality_bar,
            pass_score=request.pass_score,
            max_iterations=request.max_iterations,
        )
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"missing backend dependency: {exc.name}") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail=f"llm api connection failed: {exc}") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"llm api error: {exc}") from exc
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/run-upload")
async def run_review_upload(
    background_tasks: BackgroundTasks,
    input_a: UploadFile = File(...),
    input_b: UploadFile = File(...),
    input_c: UploadFile = File(...),
    standard_file: UploadFile = File(...),
    audit_task: str = Form("请完成动态审核并输出结构化结果"),
    quality_bar: str = Form("结果准确、可解释、可复现"),
    pass_score: int = Form(90),
    max_iterations: int = Form(3),
) -> Dict[str, Any]:
    try:
        run_id = uuid4().hex
        create_run(run_id)
        input_files = [
            await _write_upload_file(input_a, "input_a"),
            await _write_upload_file(input_b, "input_b"),
            await _write_upload_file(input_c, "input_c"),
        ]
        standard_path = await _write_upload_file(standard_file, "standard")
        add_event(
            "route",
            "上传文件已保存",
            data={"input_files": input_files, "standard_file": standard_path},
            run_id=run_id,
        )
        background_tasks.add_task(
            _run_review_job,
            run_id,
            input_files=input_files,
            standard_file=standard_path,
            audit_task=audit_task,
            quality_bar=quality_bar,
            pass_score=pass_score,
            max_iterations=max_iterations,
        )
        return {"run_id": run_id, "status": "queued"}
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=503, detail=f"missing backend dependency: {exc.name}") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail=f"llm api connection failed: {exc}") from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"llm api error: {exc}") from exc
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
