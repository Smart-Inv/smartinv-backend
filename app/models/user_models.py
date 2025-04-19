from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    "Model used for POST method: inserting user into db"
    full_name: str
    email: EmailStr
    password: str
    is_active: bool
    name_company: str
    created_at: datetime
    
class UserLogin(BaseModel):
    "Model used for GET method: logIn user"
    email: EmailStr
    password: str