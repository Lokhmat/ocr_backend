from pydantic import BaseModel, EmailStr, Field

# ---------- INPUT MODELS ----------

class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class RefreshTokenIn(BaseModel):
    refresh_token: str

# ---------- OUTPUT MODELS ----------

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
