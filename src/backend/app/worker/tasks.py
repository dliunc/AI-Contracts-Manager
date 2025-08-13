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

def extract_json_from_markdown(content: str) -> str:
    """
    Extract JSON content from markdown code blocks.
    Handles both wrapped (```json ... ```) and unwrapped JSON responses.
    """
    if not content:
        return content
    
    content = content.strip()
    
    # Check if content is wrapped in markdown code blocks
    if content.startswith('```'):
        # Find the start of JSON content (after ```json or just ```)
        lines = content.split('\n')
        start_idx = 0
        
        # Skip the opening ``` line
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                start_idx = i + 1
                break
        
        # Find the closing ``` line
        end_idx = len(lines)
        for i in range(len(lines) - 1, start_idx - 1, -1):
            if lines[i].strip() == '```':
                end_idx = i
                break
        
        # Extract content between the markers
        json_lines = lines[start_idx:end_idx]
        return '\n'.join(json_lines).strip()
    
    # Return as-is if not wrapped
    return content

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
            logger.info(f"OpenAI API call completed successfully for analysis {analysis_id}")
            
            try:
                logger.info(f"Checking OpenAI response structure for analysis {analysis_id}")
                logger.info(f"Response type: {type(response)}")
                logger.info(f"Response has choices attr: {hasattr(response, 'choices')}")
                
                if hasattr(response, 'choices'):
                    logger.info(f"Choices length: {len(response.choices)}")
                    if len(response.choices) > 0:
                        logger.info(f"First choice type: {type(response.choices[0])}")
                        logger.info(f"First choice has message attr: {hasattr(response.choices[0], 'message')}")
                        
                        if hasattr(response.choices[0], 'message'):
                            logger.info(f"Message type: {type(response.choices[0].message)}")
                            logger.info(f"Message has content attr: {hasattr(response.choices[0].message, 'content')}")
                            
                            # This is where the error might be occurring
                            logger.info(f"Attempting to access message content for analysis {analysis_id}")
                            raw_content = response.choices[0].message.content
                            logger.info(f"Successfully accessed content. Type: {type(raw_content)}, Length: {len(raw_content) if raw_content else 'None'}")
                            
                            if raw_content:
                                logger.info(f"Raw content preview: {raw_content[:200]}...")
                                
                                # Extract JSON from potential markdown wrapper
                                cleaned_content = extract_json_from_markdown(raw_content)
                                logger.info(f"Cleaned content preview: {cleaned_content[:200]}...")
                                
                                result = json.loads(cleaned_content)
                                logger.info(f"JSON parsing successful for analysis {analysis_id}")
                            else:
                                logger.error(f"OpenAI response content is None or empty for analysis {analysis_id}")
                                result = {"summary": "Empty response from AI.", "clauses": []}
                        else:
                            logger.error(f"OpenAI response choice has no message attribute for analysis {analysis_id}")
                            result = {"summary": "Invalid response structure from AI.", "clauses": []}
                    else:
                        logger.error(f"OpenAI response has no choices for analysis {analysis_id}")
                        result = {"summary": "No choices in AI response.", "clauses": []}
                else:
                    logger.error(f"OpenAI response has no choices attribute for analysis {analysis_id}")
                    result = {"summary": "Invalid response format from AI.", "clauses": []}
                    
            except Exception as parse_error:
                logger.error(f"Exception during OpenAI response processing for analysis {analysis_id}: {str(parse_error)}")
                logger.error(f"Exception type: {type(parse_error).__name__}")
                logger.error(f"Exception details: {repr(parse_error)}")
                result = {"summary": "Failed to process AI response.", "clauses": []}


            # 7. (Stretch Goal) Generate redlined docx (not implemented)

            # 8. Update analysis record with results
            logger.info(f"Attempting to update analysis record in database for analysis {analysis_id}")
            try:
                await analysis_repo.update(analysis_obj_id, AnalysisUpdate(status=AnalysisStatus.COMPLETED, result=result))
                logger.info(f"Successfully updated analysis record for analysis {analysis_id}")
            except Exception as db_error:
                logger.error(f"Database update failed for analysis {analysis_id}: {str(db_error)}")
                logger.error(f"Database error type: {type(db_error).__name__}")
                raise  # Re-raise to trigger the outer exception handler

            # Send email notification - separate from analysis completion
            logger.info(f"Starting email notification process for analysis {analysis_id}")
            try:
                logger.info(f"Fetching user {user_id} from database for email notification")
                user = await user_repo.get_by_id(user_id)
                logger.info(f"User lookup result: {'Found' if user else 'Not found'} for user {user_id}")
                
                if user:
                    logger.info(f"Checking email service configuration for analysis {analysis_id}")
                    if email_service.is_configured():
                        logger.info(f"Email service is configured, attempting to send email for analysis {analysis_id}")
                        success = email_service.send_email(
                            to_email=user.email,
                            subject="Contract Analysis Complete",
                            message=f"Your contract '{analysis.file_name}' has been successfully analyzed."
                        )
                        if success:
                            logger.info(f"Email notification sent successfully for analysis {analysis_id}")
                        else:
                            logger.warning(f"Failed to send email notification for analysis {analysis_id}")
                    else:
                        logger.info(f"Email notifications disabled or not configured for analysis {analysis_id}")
                else:
                    logger.warning(f"User {user_id} not found for email notification")
            except Exception as email_error:
                logger.error(f"Email notification failed for analysis {analysis_id}: {str(email_error)}")
                logger.error(f"Email error type: {type(email_error).__name__}")
                # Continue execution - email failure should not affect analysis completion
                
        except Exception as e:
            logger.error(f"Error analyzing contract {analysis_id}: {str(e)}")
            logger.error(f"Main exception type: {type(e).__name__}")
            logger.error(f"Exception details: {repr(e)}")
            
            try:
                logger.info(f"Attempting to update analysis status to FAILED for analysis {analysis_id}")
                await analysis_repo.update(analysis_obj_id, AnalysisUpdate(status=AnalysisStatus.FAILED))
                logger.info(f"Successfully updated analysis status to FAILED for analysis {analysis_id}")
            except Exception as db_error:
                logger.error(f"Failed to update analysis status to FAILED for analysis {analysis_id}: {str(db_error)}")
                logger.error(f"Database error in failure handler type: {type(db_error).__name__}")
            
            # Try to send failure notification email, but don't let it fail the task
            try:
                logger.info(f"Attempting to send failure notification email for analysis {analysis_id}")
                user = await user_repo.get_by_id(user_id)
                if user and email_service.is_configured():
                    email_service.send_email(
                        to_email=user.email,
                        subject="Contract Analysis Failed",
                        message=f"Unfortunately, the analysis of your contract '{analysis.file_name if 'analysis' in locals() else 'Unknown'}' has failed. Please try again or contact support."
                    )
                    logger.info(f"Failure notification email sent for analysis {analysis_id}")
            except Exception as email_error:
                logger.error(f"Failed to send failure notification email for analysis {analysis_id}: {str(email_error)}")
                logger.error(f"Failure email error type: {type(email_error).__name__}")
        finally:
            logger.info(f"Analysis task finished for analysis_id: {analysis_id}")

    asyncio.get_event_loop().run_until_complete(main())
    return {"status": "Completed", "analysis_id": analysis_id}