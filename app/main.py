from fastapi import FastAPI
from firestore_client import db
from routers import users, tokens

app = FastAPI()

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(tokens.router, prefix="/api", tags=["tokens"])

