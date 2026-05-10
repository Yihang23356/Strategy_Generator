from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from routes import review_router


app = FastAPI(title="Strategy Planner Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
