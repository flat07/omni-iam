# main.py
from fastapi import FastAPI
from app.api.v1 import auth

app = FastAPI(title="Omni IAM")

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])


@app.get("/")
def root():
    return {"message": "Omni IAM API running"}