from db.models import User, PushSubscription
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.crypto import get_password_hash
from schemas.user import UserCreate, PushSubscriptionCreate
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


async def save_push_subscription(db: AsyncSession, user_id: UUID, sub_data: PushSubscriptionCreate):
    # Проверяем, есть ли уже этот браузер в базе
    query = select(PushSubscription).where(PushSubscription.endpoint == sub_data.endpoint)
    result = await db.execute(query)
    if not result.scalar_one_or_none():
        sub = PushSubscription(
            user_id=user_id,
            endpoint=sub_data.endpoint,
            p256dh=sub_data.keys.p256dh,
            auth=sub_data.keys.auth
        )
        db.add(sub)
        await db.commit()


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

async def get_user_subscriptions(db: AsyncSession, user_id: UUID):
    query = select(PushSubscription).where(PushSubscription.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()