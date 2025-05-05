
INSERT INTO app.tokens (user_id, token, expires_at)
VALUES (:user_id, :token, :expires_at)
RETURNING token, expires_at;
