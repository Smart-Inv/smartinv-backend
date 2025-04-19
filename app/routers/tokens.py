from fastapi import APIRouter

router = APIRouter()

# generate a random JWT token
@router.get("/get_token", tags=["tokens"])
async def get_token():
    pass