SELECT id, s3_key, status, result_json, created_at
FROM app.images
WHERE user_id = :user_id AND (:cursor_timestamp IS NULL OR created_at < :cursor_timestamp)
ORDER BY created_at DESC
LIMIT :limit;
