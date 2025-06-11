from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TokenCreateRequest(BaseModel):
    days_valid: Optional[int] = Field(
        None,
        description="Number of days the token should be valid for. If not specified, token will be infinite",
    )


class TokenResponse(BaseModel):
    token: str = Field(..., description="Generated API token")
    expires_at: Optional[datetime] = Field(
        None, description="Token expiration date. None if token is infinite"
    )
