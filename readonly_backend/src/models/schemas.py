from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class ImageStatus(BaseModel):
    image_id: str
    s3_key: str
    status: str
    result_json: str
    created_at: datetime

class PaginatedImageResponse(BaseModel):
    images: List[ImageStatus]
    next_cursor: Optional[str] = None

class ImageListParams(BaseModel):
    cursor: Optional[str] = None
    limit: int = 10
