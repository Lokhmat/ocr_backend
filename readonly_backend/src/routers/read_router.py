from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from ..models.connector import DBConnector
from ..auth.security import get_current_user
from ..models.schemas import PaginatedImageResponse, ImageListParams
from ..models.image import get_by_user, get_by_id

read_router = APIRouter(tags=["read"], prefix="/api")

@read_router.post("/list", response_model=PaginatedImageResponse)
async def list_images(
    params: ImageListParams,
    user_id: str =  Depends(get_current_user)):
    images, next_cursor = get_by_user(user_id, params.cursor, params.limit)
    
    return PaginatedImageResponse(
        images=images,
        next_cursor=next_cursor
    )

@read_router.get("/image")
async def get_image_data(image_id: str, _: str = Depends(get_current_user)):
    image = get_by_id(image_id)
    return image
