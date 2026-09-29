from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from database.database_models import User
from schemas.schemas import UserLogin, Token
from core.auth import verify_password, create_access_token


router = APIRouter()


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.Email == login_data.email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_access_token(user.UserID)

    return {
        "access_token": token,
        "token_type": "bearer"
    }