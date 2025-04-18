from fastapi import APIRouter, HTTPException
from firestore_client import db
from google.api_core.exceptions import GoogleAPIError
from datetime import datetime

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
async def add_user(full_name: str,
                   email: str, 
                   password: str, 
                   is_active: bool,
                   name_company: str,
                   created_at: datetime):
    try:
        # TODO: Implement real password hashing
        hashed_password = password

        doc_ref = db.collection("users").document()
        doc_ref.set({
            "full_name": full_name,
            "email": email,
            "hashed_password": hashed_password,
            "is_active": is_active,
            "name_company": name_company,
            "created_at": created_at
        })

        return {"id": doc_ref.id}, status_code.HTTP_201_CREATED
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"Firestore error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
