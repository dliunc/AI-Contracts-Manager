import asyncio
import logging
import os
from app.worker.celery_app import celery_app
from app.models.analysis import AnalysisStatus
from app.schemas.analysis import AnalysisUpdate
from app.core.config import settings
import openai
import docx
import pypdf
from bson import ObjectId


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_contract_content(file_path: str) -> str:
    """Reads content from .docx or .pdf file."""
    if file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            return "\n".join([page.extract_text() for page in pdf_reader.pages])
    else:
        raise ValueError("Unsupported file type")

@celery_app.task(bind=True)
def analyze_contract(self, analysis_id: str, user_id: str):
    """
    A Celery task to analyze a contract.
    """
    from app.services.analysis_service import AnalysisService
    from app.services.email_service import EmailService
    from app.db.repositories.user_repository import UserRepository
    from app.db.repositories.analysis_repository import AnalysisRepository

    async def main():
        logger.info(f"Starting analysis for analysis_id: {analysis_id}")
        analysis_repo = AnalysisRepository()
        user_repo = UserRepository()
        email_service = EmailService()
        
        analysis_obj_id = ObjectId(analysis_id)

        try:
            # 1. Fetch the ContractAnalysis record
            analysis = await analysis_repo.get(analysis_id)
            if not analysis:
                logger.error(f"Analysis with id {analysis_id} not found.")
                return

            # 2. Update status to "processing"
            await analysis_repo.update(analysis_obj_id, AnalysisUpdate(status=AnalysisStatus.IN_PROGRESS))

            # 3. Read contract content
            file_path = analysis.s3_path
            contract_text = read_contract_content(file_path)

            # 4. Construct prompt for LLM
            prompt = f"""
            Analyze the following contract and return your analysis in JSON format.
            The JSON object should have two keys: "summary" and "clauses".
            - "summary": A brief summary of the contract.
            - "clauses": A list of key clauses found in the contract.

            Contract Text:
            {contract_text}
            """

            # 5. Call OpenAI API
            # Use OpenAI Python SDK v1+ interface
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful legal assistant that provides analysis in JSON format."},
                    {"role": "user", "content": prompt},
                ],
            )

            # 6. Parse LLM response
            import json
            try:
                result = json.loads(response.choices[0].message.content)
            except (json.JSONDecodeError, KeyError):
                logger.error(f"Failed to parse JSON response from OpenAI for analysis {analysis_id}")
                result = {"summary": "Failed to parse analysis from AI.", "clauses": []}


            # 7. (Stretch Goal) Generate redlined docx (not implemented)

            # 8. Update analysis record with results
            await analysis_repo.update(analysis_obj_id, AnalysisUpdate(status=AnalysisStatus.COMPLETED, result=result))

            # Send email notification
            user = await user_repo.get_by_id(user_id)
            if user:
                email_service.send_email(
                    to_email=user.email,
                    subject="Contract Analysis Complete",
                    message=f"Your contract '{analysis.file_name}' has been successfully analyzed."
                )
        except Exception as e:
            logger.error(f"Error analyzing contract {analysis_id}: {e}")
            await analysis_repo.update(analysis_obj_id, AnalysisUpdate(status=AnalysisStatus.FAILED))
            # Optionally, send a failure notification email
        finally:
            logger.info(f"Analysis task finished for analysis_id: {analysis_id}")

    asyncio.get_event_loop().run_until_complete(main())
    return {"status": "Completed", "analysis_id": analysis_id}