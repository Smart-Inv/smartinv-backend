from fastapi import APIRouter, HTTPException
from firestore_client import db
from google.api_core.exceptions import GoogleAPIError
import bcrypt

from models.user_models import *
from utils.token_generation import *

router = APIRouter()

# Retrieve all the active users from the database
@router.get("/get_users/", tags=["users"])
async def get_users(token: str = Depends(get_current_user)):
    try:
        query = db.collection("users").where("is_active", "==", True)
        users = query.stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in users]
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"Firestore error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Adds a new user to the database
@router.post("/register_user/", tags=["users"])
async def register_user(user: UserCreate):
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
    
@router.post("/login", tags=["users"])
async def login(user: UserLogin):
    try:
        users_ref = db.collection("users")
        query = users_ref.where("email", "==", user.email).limit(1).stream()
        user_doc = next(query, None)
        if user_doc is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_data = user_doc.to_dict()
        hashed_password = user_data.get("hashed_password")

        if not bcrypt.checkpw(user.password.encode(), hashed_password.encode()):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token_data = {
            "sub": user_doc.id,
            "email": user_data["email"],
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"Firestore error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
