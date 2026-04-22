from fastapi import utils, Depends, Request, HTTPException, status, Request
from db.sessions import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from utils.crypto import decode_access_token
from uuid import UUID
from crud.user import get_user_by_id


async def get_current_user(request: Request,db: AsyncSession = Depends(get_db)) -> UUID:
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
            
        )
    cookie = request.cookies.get("access_token")
    if not cookie:
        raise credentials_exception
    user_id = decode_access_token(cookie)
    user = await get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception
    return user