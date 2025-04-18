from fastapi import FastAPI
from firestore_client import db
from routers import users

app = FastAPI()

app.include_router(users.router, prefix="/api", tags=["users"])
