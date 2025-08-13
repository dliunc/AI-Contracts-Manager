from app.db.repository import BaseRepository
from app.models.analysis import ContractAnalysis

class AnalysisRepository(BaseRepository[ContractAnalysis]):
    def __init__(self):
        super().__init__(collection_name="analyses", model=ContractAnalysis)