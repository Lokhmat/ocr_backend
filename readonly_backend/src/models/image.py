from typing import Tuple, List
from datetime import datetime

from sqlalchemy import text

from ..models.schemas import ImageStatus
from ..models.connector import connector
from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

def get_by_user(user_id: str, cursor: str = None, limit: int = 10) -> Tuple[List[ImageStatus], str]:
        """
        Get paginated images for a specific user.
        Returns: (images, next_cursor)
        """
        with connector.engine.begin() as conn:
            # If cursor is provided, parse it as timestamp
            cursor_timestamp = None
            if cursor:
                try:
                    cursor_timestamp = datetime.fromisoformat(cursor)
                except ValueError:
                    cursor_timestamp = None

            select_sql = open(f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/images_get_by_user.sql").read()
            query = text(select_sql)
            
            params = {"user_id": user_id, "limit": limit, "cursor_timestamp": cursor_timestamp}
            
            results = conn.execute(query, params).fetchall()
            
            # Get the next cursor (timestamp of the last record)
            next_cursor = None
            if results:
                next_cursor = results[-1].created_at.isoformat()

            images = [
                ImageStatus(
                    image_id=str(row.id),
                    s3_key=str(row.s3_key),
                    status=str(row.status),
                    result_json=str(row.result_json),
                    created_at=row.created_at
                )
                for row in results
            ]
            
            return images, next_cursor 
        
def get_by_id(image_id: str) -> ImageStatus:
        """
        Get image by it's id.
        Returns: ImageStatus
        """
        with connector.engine.begin() as conn:
            select_sql = open(f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/images_get_by_id.sql").read()
            query = text(select_sql)
            
            params = {"image_id": image_id}
            
            result = conn.execute(query, params).fetchone()
            
            if not result:
                return None
                
            return ImageStatus(
                image_id=str(result.id),
                s3_key=str(result.s3_key), 
                status=str(result.status),
                result_json=str(result.result_json),
                created_at=result.created_at
            )
