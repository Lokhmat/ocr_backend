import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

def generate_token() -> str:
    return str(uuid.uuid4())

def create_token(connector, user_id: str, days_valid: Optional[int] = None) -> dict:
    with connector.engine.begin() as conn:
        token = generate_token()
        expires_at = None
        if days_valid is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)
        
        with open(f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/tokens_create.sql") as f:
            query = text(f.read())
            conn.execute(
                query,
                {
                    "user_id": user_id,
                    "token": token,
                    "expires_at": expires_at
                }
            ).fetchone()
        
        return {
            "token": token,
            "expires_at": expires_at.isoformat() if expires_at else None
        }
