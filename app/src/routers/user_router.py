from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..models.connector import connector
from ..models import user
from ..auth.security import get_current_user

user_router = APIRouter(tags=["user"])


class CloudKeyUpdate(BaseModel):
    cloud_key: str


class CloudKeyResponse(BaseModel):
    id: str
    cloud_key: str | None


@user_router.put("/user/cloud-key", response_model=CloudKeyResponse)
async def update_cloud_key(
    key_update: CloudKeyUpdate, current_user: str = Depends(get_current_user)
):
    with connector.engine.begin() as conn:
        result = user.update_cloud_key(conn, current_user, key_update.cloud_key)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return CloudKeyResponse(id=result.id, cloud_key=result.cloud_key)


@user_router.get("/user/cloud-key", response_model=CloudKeyResponse)
async def get_cloud_key(current_user: str = Depends(get_current_user)):
    with connector.engine.begin() as conn:
        result = user.get_cloud_key(conn, current_user)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return CloudKeyResponse(id=result.id, cloud_key=result.cloud_key)
