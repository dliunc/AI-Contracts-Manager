from pydantic import BaseModel, Field, EmailStr
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    hashed_password: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "user123",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "hashed_password": "a_very_secure_password_hash"
            }
        }