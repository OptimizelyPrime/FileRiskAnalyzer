import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from ..business_logic import refactor_pipeline
from fastapi.middleware.cors import CORSMiddleware

class RefactorRequest(BaseModel):
    repo_url: str = Field(..., min_length=1)
    branch: str
    files: List[str] = Field(..., min_length=1)

app = FastAPI()

# Basic logger for API-specific messages
logger = logging.getLogger("refactor_api")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# Enable CORS for local development and cross-origin clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/refactor", status_code=status.HTTP_202_ACCEPTED)
async def refactor(request: RefactorRequest):
    """
    This endpoint initiates the refactoring process.
    """
    logger.info(
        "Refactor request received repo_url=%s branch=%s files=%s",
        request.repo_url,
        request.branch,
        request.files,
    )
    try:
        refactor_pipeline.run(request.repo_url, request.branch, request.files)
        logger.info("Refactor pipeline completed successfully")
        return {"status": "Refactoring process initiated"}
    except Exception as e:
        logger.exception("Refactor pipeline failed")
        raise HTTPException(status_code=500, detail=f"Refactor pipeline failed: {e}")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "ok"}
