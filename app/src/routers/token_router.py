from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.token import create_token
from ..models.connector import connector
from ..token.schemas import TokenResponse, TokenCreateRequest
from ..auth.security import get_current_user

token_router = APIRouter(tags=["token"])


@token_router.post("/token", response_model=TokenResponse)
async def create_token_endpoint(
    request: TokenCreateRequest, user_id: str = Depends(get_current_user)
):
    try:
        result = create_token(connector, user_id, request.days_valid)
        return TokenResponse(token=result["token"], expires_at=result["expires_at"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
