INSERT INTO app.users (id, email, hashed_password)
VALUES (:user_id, :email, :hashed_password)
RETURNING id, email;
