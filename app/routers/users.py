from fastapi import APIRouter, HTTPException
from firestore_client import db
from google.api_core.exceptions import GoogleAPIError
import bcrypt

from models.user_models import *

router = APIRouter()

# Retrieve all the active users from the database
@router.get("/get_users/", tags=["users"])
async def get_users():
    try:
        query = db.collection("users").where("is_active", "==", True)
        users = query.stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in users]
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"Firestore error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Adds a new user to the database
@router.post("/add_user/", tags=["users"])
async def add_user(user: UserCreate):
    try:
        hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

        doc_ref = db.collection("users").document()
        doc_ref.set({
            "full_name": user.full_name,
            "email": user.email,
            "hashed_password": hashed,
            "is_active": user.is_active,
            "name_company": user.name_company,
            "created_at": user.created_at
        })

        return {"id": doc_ref.id}
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"Firestore error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
