from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime