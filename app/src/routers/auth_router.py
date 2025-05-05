from fastapi import APIRouter, HTTPException, status
from ..models.connector import connector
from ..models import user
from ..auth import security
from ..auth.schemas import UserRegisterIn, UserLoginIn, TokenOut, RefreshTokenIn

auth_router = APIRouter(tags=["auth"])

@auth_router.post("/register", response_model=TokenOut)
async def register(user_input: UserRegisterIn):
    with connector.engine.begin() as conn:
        if user.get_user_by_email(conn, user_input.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = user.create_user(conn, user_input.email, user_input.password)
        access_token = security.create_access_token({"sub": str(new_user.id)})
        refresh_token = security.create_refresh_token({"sub": str(new_user.id)})

        return {"access_token": access_token, "refresh_token": refresh_token}

@auth_router.post("/login", response_model=TokenOut)
async def login(user_input: UserLoginIn):
    with connector.engine.begin() as conn:
        db_user = user.get_user_by_email(conn, user_input.email)
        if not db_user or not user.verify_password(user_input.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = security.create_access_token({"sub": str(db_user.id)})
        refresh_token = security.create_refresh_token({"sub": str(db_user.id)})

        return {"access_token": access_token, "refresh_token": refresh_token}

@auth_router.post("/refresh", response_model=TokenOut)
async def refresh_token(data: RefreshTokenIn):
    token = data.refresh_token
    payload = security.verify_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = security.create_access_token({"sub": str(payload["sub"])})
    new_refresh_token = security.create_refresh_token({"sub": str(payload["sub"])})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
