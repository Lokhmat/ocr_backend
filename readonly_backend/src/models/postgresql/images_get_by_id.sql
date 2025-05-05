SELECT *
FROM app.images
WHERE id = :image_id
LIMIT 1;
