# main.py
from fastapi import FastAPI
from app.api.v1 import auth, users, org

app = FastAPI(title="Omni IAM")

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(org.router, prefix="/api/v1", tags=["organization"])

@app.get("/")
def root():
    return {"message": "Omni IAM API running"}
