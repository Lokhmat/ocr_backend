INSERT INTO app.images (user_id, s3_key, status, workload)
VALUES (:user_id, :s3_key, 'created', :workload)
RETURNING id, user_id, s3_key, status, workload, result_json, created_at;
