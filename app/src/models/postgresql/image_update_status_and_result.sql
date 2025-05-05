UPDATE app.images
SET status = :status, result_json = :result_json, status_reason=:status_reason
WHERE id = :image_id;
