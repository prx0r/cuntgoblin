"""{{PRODUCT_NAME}} API — FastAPI application."""

from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI(
    title="{{PRODUCT_NAME}}",
    description="{{PRODUCT_DESCRIPTION}}",
    version="0.1.0",
)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "{{PRODUCT_NAME}}",
        "version": "0.1.0",
        "status": "ok",
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}
