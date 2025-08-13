from app.db.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import AnalysisCreate, Analysis
from app.models.analysis import ContractAnalysis
from app.worker.tasks import analyze_contract

class AnalysisService:
    def __init__(self):
        self.repository = AnalysisRepository()

    async def create_analysis(self, analysis_data: AnalysisCreate) -> Analysis:
        analysis = ContractAnalysis(**analysis_data.model_dump())
        created_analysis = await self.repository.create(analysis)
        analyze_contract.delay(analysis_id=str(analysis.id), user_id=str(analysis.user_id))
        return Analysis.model_validate(created_analysis)

    async def get_analysis(self, analysis_id: str) -> Analysis:
        analysis = await self.repository.get(analysis_id)
        if analysis:
            return Analysis.model_validate(analysis)
        return None