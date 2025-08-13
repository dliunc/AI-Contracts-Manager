import asyncio
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import Analysis, AnalysisCreate
from typing import List
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()
UPLOAD_DIRECTORY = "/tmp/uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def get_analysis_service():
    return AnalysisService()

@router.post("/", response_model=List[Analysis], response_model_by_alias=False)
async def create_analysis(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service)
):
    async def process_file(file: UploadFile):
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        analysis_data = AnalysisCreate(
            user_id=current_user.id,
            file_name=file.filename,
            s3_path=file_path  # Using s3_path to store local path for now
        )
        return await service.create_analysis(analysis_data)

    tasks = [process_file(file) for file in files]
    analyses = await asyncio.gather(*tasks)
    return analyses

@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis(
    analysis_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    analysis = await service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis