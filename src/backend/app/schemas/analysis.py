from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.analysis import AnalysisStatus
from app.models.custom_types import PyObjectId

class AnalysisBase(BaseModel):
    file_name: str

class AnalysisCreate(AnalysisBase):
    user_id: str
    s3_path: str

class AnalysisUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[dict] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AnalysisInDB(AnalysisBase):
    id: PyObjectId
    user_id: str
    s3_path: str
    status: str
    result: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str
        }

class Analysis(AnalysisInDB):
    pass