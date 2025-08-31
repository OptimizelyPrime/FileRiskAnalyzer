from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from src.business_logic import refactor_pipeline

class RefactorRequest(BaseModel):
    repo_url: str = Field(..., min_length=1)
    branch: str
    files: List[str] = Field(..., min_length=1)

app = FastAPI()

@app.post("/api/refactor", status_code=status.HTTP_202_ACCEPTED)
async def refactor(request: RefactorRequest):
    """
    This endpoint initiates the refactoring process.
    """
    try:
        refactor_pipeline.run(request.repo_url, request.branch, request.files)
        return {"status": "Refactoring process initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
