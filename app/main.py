from fastapi import FastAPI
from app.firestore_client import db
from app.routers import users, tokens, model_prediction, buckets

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
app.include_router(model_prediction.router, prefix="/api", tags=["model"])
app.include_router(buckets.router, prefix="/api", tags=["buckets"])


