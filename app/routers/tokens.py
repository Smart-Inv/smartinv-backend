from fastapi import APIRouter, HTTPException, status, Body
from app.utils.token_generation import *

import logging

router = APIRouter()

# generate a random JWT token
@router.post("/refresh_token", tags=["tokens"])
async def refresh_token(refresh_token: str = Body(...)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        new_access_token = create_access_token({"sub": user_id, "email": email})
        new_refresh_token = create_refresh_token({"sub": user_id, "email": email})

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")