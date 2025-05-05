import hashlib
import uuid

from sqlalchemy import text

from ..constants import BASE_POSTGRES_TRANSACTIONS_DIRECTORY

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_user(connection, email: str, password: str):
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)
    with open(f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/user_create.sql") as f:
        query = text(f.read())
        return connection.execute(query, {"user_id": user_id, "email": email, "hashed_password": hashed_password}).fetchone()

def get_user_by_email(connection, email: str):
    with open(f"{BASE_POSTGRES_TRANSACTIONS_DIRECTORY}/user_get_by_email.sql") as f:
        query = text(f.read())
        return connection.execute(query, {"email": email}).fetchone()
