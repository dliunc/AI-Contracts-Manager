from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.custom_types import PyObjectId

class AnalysisStatus:
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ContractAnalysis(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    file_name: str
    s3_path: str
    status: str = Field(default=AnalysisStatus.PENDING)
    result: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "60d5ec49e7afde3a_dummy_id_for_example",
                "user_id": "user123",
                "file_name": "contract.pdf",
                "s3_path": "s3://my-bucket/contracts/contract.pdf",
                "status": "COMPLETED",
                "result": {"summary": "This is a summary.", "clauses": []},
                "created_at": "2025-08-11T10:00:00Z",
                "updated_at": "2025-08-11T10:05:00Z"
            }
        }