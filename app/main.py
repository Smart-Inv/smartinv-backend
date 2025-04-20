from fastapi import FastAPI
from app.firestore_client import db
from routers import users, tokens

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TODO: need to change this 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(tokens.router, prefix="/api", tags=["tokens"])

