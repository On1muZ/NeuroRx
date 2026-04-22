from db.models import User
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.crypto import get_password_hash
from schemas.user import UserCreate
from uuid import UUID


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    user = User(username=user.username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user


async def change_user_password(db: AsyncSession, user_id: UUID, new_password: str):
    hashed_password = get_password_hash(new_password)
    query = update(User).where(User.id == user_id).values(hashed_password=hashed_password)
    await db.execute(query)
    await db.commit()


async def delete_user(db: AsyncSession, user_id: UUID):
    query = delete(User).where(User.id == user_id)
    await db.execute(query)
    await db.commit()


async def get_user_by_id(db: AsyncSession, user_id: UUID):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user