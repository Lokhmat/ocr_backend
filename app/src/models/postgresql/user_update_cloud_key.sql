UPDATE app.users
SET cloud_key = :cloud_key
WHERE id = :user_id
RETURNING id, cloud_key; 