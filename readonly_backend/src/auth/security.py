import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text

from ..models.connector import connector

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(request: Request):
    credentials: HTTPAuthorizationCredentials = await security_scheme(request)
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    user_id = get_user_id(connector, token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user_id  # return user id

def get_user_id(connector, token: str):
    with connector.engine.begin() as conn:     
        with open(f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/get_user_id.sql") as f:
            query = text(f.read())
            result = conn.execute(
                query,
                {
                    "token": token,
                }
            ).fetchone()

            return result.user_id if result else None
        
    
