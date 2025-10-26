import logging
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import List, Union
from ..business_logic import refactor_pipeline
from fastapi.middleware.cors import CORSMiddleware

class RefactorRequest(BaseModel):
    repo_url: str = Field(..., min_length=1)
    branch: str = Field(default="main")
    # Accept either a single string or a list of strings; normalize in handler
    files: Union[List[str], str]

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
    # Normalize files to a non-empty list
    files: List[str] = request.files if isinstance(request.files, list) else [request.files]
    files = [f for f in (s.strip() for s in files) if f]
    if not files:
        raise HTTPException(status_code=422, detail="'files' must be a non-empty list or string")

    try:
        refactor_pipeline.run(request.repo_url, request.branch, files)
        logger.info("Refactor pipeline completed successfully")
        return {"status": "Refactoring process initiated"}
    except Exception as e:
        logger.exception("Refactor pipeline failed")
        raise HTTPException(status_code=500, detail=f"Refactor pipeline failed: {e}")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, exc: RequestValidationError):
    # Log structured validation errors for easier debugging
    try:
        logger.warning("Validation error on %s %s: %s", req.method, req.url.path, exc.errors())
    except Exception:
        logger.warning("Validation error: %s", exc)
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
