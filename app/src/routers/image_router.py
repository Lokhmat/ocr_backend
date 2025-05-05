from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import io
import os

from ..bucket_init import s3, bucket_name
from ..auth.security import get_current_user
from ..models.image import Image

image_router = APIRouter(tags=["Image"])

@image_router.get("/get-image")
async def get_image(image_id: str):
    try:
        image_model = Image()
        image = image_model.get_by_id(image_id)
        # Get the image from S3
        response = s3.get_object(Bucket=bucket_name, Key=image.s3_key)
        
        # Extract original filename from s3_key
        original_filename = image.s3_key.split('/')[-1]
        
        # Create a streaming response with filename in headers
        return StreamingResponse(
            io.BytesIO(response['Body'].read()),
            media_type=response['ContentType'],
            headers={
                'Content-Disposition': f'attachment; filename="{original_filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}") 