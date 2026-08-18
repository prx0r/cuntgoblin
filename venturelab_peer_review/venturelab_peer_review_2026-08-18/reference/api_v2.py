from __future__ import annotations
from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="VentureLab API", version="0.2.0")
SYSTEM = None

class JobCreate(BaseModel):
    factory_type: str
    task_kind: str
    input: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str
    budget_usd: float | None = None
    quality_floor: float = Field(default=.70, ge=0, le=1)

def system():
    if SYSTEM is None:
        raise RuntimeError("VentureLab system not initialized")
    return SYSTEM

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/status")
def status():
    return system().get_status()

@app.post("/jobs", status_code=202)
def create_job(req: JobCreate):
    job = system().submit_job(req.model_dump())
    return {"job_id": job["id"], "state": job["state"]}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = system().get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job

@app.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    result = system().cancel_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="job not found")
    return result
