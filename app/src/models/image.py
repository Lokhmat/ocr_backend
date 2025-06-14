from typing import List, Tuple
import json
from sqlalchemy import text
from datetime import datetime

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY
from .connector import connector
from ..process.schemas import ImageStatus


class Image:
    def create(self, user_id: str, s3_key: str, workload: str) -> dict:
        """Create a new image record in the database."""
        with connector.engine.begin() as conn:
            insert_sql = open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/image_insert.sql"
            ).read()
            query = text(insert_sql)
            result = conn.execute(
                query,
                {
                    "user_id": user_id,
                    "s3_key": s3_key,
                    "workload": workload,
                },
            ).fetchone()
            return {"id": result.id, "status": result.status}

    def update_status(self, image_id: str, status: str, result_json: dict = None):
        """Update the status and result of an image."""
        with connector.engine.begin() as conn:
            update_sql = open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/image_update_status_and_result.sql"
            ).read()
            query = text(update_sql)
            conn.execute(
                query,
                {
                    "image_id": image_id,
                    "status": status,
                    "status_reason": None,
                    "result_json": json.dumps(result_json) if result_json else "{}",
                },
            )

    def update_error(self, image_id: str, error_reason: str, result_json: dict = None):
        """Update the status and result of an image."""
        with connector.engine.begin() as conn:
            update_sql = open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/image_update_status_and_result.sql"
            ).read()
            query = text(update_sql)
            conn.execute(
                query,
                {
                    "image_id": image_id,
                    "status": "error",
                    "status_reason": error_reason,
                    "result_json": json.dumps(result_json) if result_json else "{}",
                },
            )

    def get_by_user(
        self, user_id: str, cursor: str = None, limit: int = 10
    ) -> Tuple[List[ImageStatus], str]:
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

            select_sql = open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/images_get_by_user.sql"
            ).read()
            query = text(select_sql)

            params = {
                "user_id": user_id,
                "limit": limit,
                "cursor_timestamp": cursor_timestamp,
            }

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
                    result_json=json.dumps(row.result_json),
                    created_at=row.created_at,
                )
                for row in results
            ]

            return images, next_cursor

    def get_by_id(self, image_id: str) -> ImageStatus:
        """
        Get image by it's id.
        Returns: ImageStatus
        """
        with connector.engine.begin() as conn:
            select_sql = open(
                f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/images_get_by_id.sql"
            ).read()
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
                created_at=result.created_at,
            )
