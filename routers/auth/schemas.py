from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str

class UserInfoCheck(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class User(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    zipcode: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None

    class Config:
        orm_mode = True

class UserCreate(User):
    password: str
    is_active: bool = False
    is_staff: bool = False


class UserUpdate(User):
    pass

class Login(BaseModel):
    username: str
    password: str

class UserPassword(BaseModel):
    oldPassword: str
    password: str
