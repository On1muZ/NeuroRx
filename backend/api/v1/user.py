from db.models import User
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from db.sessions import get_db
from fastapi import Depends, APIRouter, HTTPException, status, Response
from schemas.user import UserCreate, User
from crud.user import create_user, get_user_by_username, delete_user as crud_delete_user
from sqlalchemy.exc import IntegrityError
from api.deps import get_current_user
from utils.crypto import verify_password, create_access_token 



router = APIRouter(prefix="/users")


@router.post("/signup")
async def signup_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        await create_user(db, user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This username has already taken. Try another one")
    else:
        raise HTTPException(status_code=status.HTTP_201_CREATED)
    


@router.post("/login")
async def login_user(user: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        user_from_db = await get_user_by_username(db, user.username)
        if user_from_db is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password")
        elif not verify_password(user.password, user_from_db.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password")
        else:
            token = create_access_token(user_from_db.id)
            response.set_cookie(key="access_token", value=token, httponly=True)
            return {"access_token": token, "token_type": "bearer"}
    except TypeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect username or password")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return User(
        id=current_user.id,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.delete("/delete")
async def delete_user(response: Response, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await crud_delete_user(db, current_user.id)
    response.delete_cookie(key="access_token", path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response