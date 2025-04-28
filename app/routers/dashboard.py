import requests
from fastapi import APIRouter, HTTPException, Depends, Query
from app.firestore_client import db
from google.api_core.exceptions import GoogleAPIError

from app.models.user_models import *
from app.routers.model_prediction import *
from app.utils.token_generation import *

router = APIRouter()

# Retrieve all the active users from the database
@router.get("/dashboard_data/", tags=["dashboard"])
async def dashboard_data(token: str = Depends(oauth2_scheme),
                         current_user: dict = Depends(get_current_user)):    
    try:
        email = current_user["email"]
        query = db.collection("users").where("email", "==", email).limit(1).stream()
        user_doc = next(query, None)
        
        if user_doc is None:
            raise HTTPException(status_code=404, detail="User not found.")

        user_data = user_doc.to_dict()

        name_company = user_data.get("name_company").replace(' ', '').lower()
        
        values = await predict_values(token, name_company)

        return {"response": values}
    
    except GoogleAPIError as e:
        raise HTTPException(status_code=500, detail=f"Firestore error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")