import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Query
from typing import List
import boto3
import tempfile

from ..auth.security import get_current_user
from ..process.schemas import ImageUploadResponse, ImageStatus, PaginatedImageResponse, ImageListParams
from ..models.image import Image
from ..process.image_processor import extract_json_from_image_cloud, extract_json_from_image_premise

process_router = APIRouter(tags=["process"])

# S3 client config
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET_KEY"],
)
S3_BUCKET = os.environ["S3_BUCKET"]

def background_processing(image_id: str, s3_key: str, workload: str):
    image_model = Image()
    try:
        # Update status to in_process
        print("Updated to in_process")
        image_model.update_status(image_id, "in_process")
        
        # Download image from S3 to temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            s3.download_file(S3_BUCKET, s3_key, temp_file.name)
            
            # Process image and extract JSON
            if workload == "cloud":
                extracted_data = extract_json_from_image_cloud(temp_file.name)
            else:
                extracted_data = extract_json_from_image_premise(temp_file.name)
            # Update status to finished
            image_model.update_status(image_id, "finished", extracted_data)
            
    except Exception as e:
        # Update status to error if something goes wrong
        image_model.update_status(image_id, "error")
        image_model.update_error(image_id, str(e))
        raise

@process_router.post("/upload-images", response_model=List[ImageUploadResponse])
async def upload_images(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    workload: str = "cloud",
    current_user: str = Depends(get_current_user)
):
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed.")

    image_model = Image()
    results = []

    for file in files:
        file_id = str(uuid.uuid4())
        s3_key = f"{current_user}/{file_id}/{file.filename}"

        # Upload to S3
        s3.upload_fileobj(file.file, S3_BUCKET, s3_key)

        # Create image record
        result = image_model.create(current_user, s3_key, workload)
        results.append(ImageUploadResponse(image_id=result["id"], status=result["status"]))

        # Background task to process image
        background_tasks.add_task(background_processing, str(result["id"]), s3_key, workload)

    return results

@process_router.get("/images/list", response_model=PaginatedImageResponse)
async def get_image_list(
    current_user: str = Depends(get_current_user),
    cursor: str = None,
    limit: int = Query(10, ge=1, le=100)
):
    image_model = Image()
    images, next_cursor = image_model.get_by_user(current_user, cursor, limit)
    
    return PaginatedImageResponse(
        images=images,
        next_cursor=next_cursor
    )
