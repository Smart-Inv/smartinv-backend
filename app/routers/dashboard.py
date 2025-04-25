from fastapi import APIRouter, HTTPException
from app.firestore_client import db
from google.api_core.exceptions import GoogleAPIError

from app.models.user_models import *
from app.utils.token_generation import *

router = APIRouter()

# Retrieve all the active users from the database
@router.get("/dashboard_data/", tags=["dashboard"])
async def dashboard_data(token: str = Depends(get_current_user)):
    print("we are here!!")
    return {"response": "works!"}