# main.py
from fastapi import FastAPI
from app.api.v1 import auth, users

app = FastAPI(title="Omni IAM")

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])

@app.get("/")
def root():
    return {"message": "Omni IAM API running"}
