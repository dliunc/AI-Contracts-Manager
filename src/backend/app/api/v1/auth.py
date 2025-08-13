from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, User, Token

router = APIRouter()

def get_auth_service():
    return AuthService()

@router.post("/register", response_model=User)
async def register_user(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    return await service.create_user(user_data)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db)
):
    user = await service.user_repo.get_by_username(db, username=form_data.username)
    if not user or not service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}