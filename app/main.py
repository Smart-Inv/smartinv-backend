from fastapi import FastAPI
from app.firestore_client import db
from app.routers import users, tokens, model_prediction, buckets, dashboard

from fastapi.middleware.cors import CORSMiddleware

API_PREFIX = "/api"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://smartinv.es", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix=API_PREFIX, tags=["users"])
app.include_router(tokens.router, prefix=API_PREFIX, tags=["tokens"])
app.include_router(model_prediction.router, prefix=API_PREFIX, tags=["model"])
app.include_router(buckets.router, prefix=API_PREFIX, tags=["buckets"])
app.include_router(dashboard.router, prefix=API_PREFIX, tags=["dashboard"])


