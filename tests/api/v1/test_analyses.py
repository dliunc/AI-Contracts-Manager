import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.user import User
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_create_analysis_success(client: AsyncClient, db_session: AsyncSession, test_user: User):
    auth_service = AuthService()
    token = auth_service.create_access_token(data={"sub": test_user.username})

    files = {"files": ("test.txt", b"test content", "text/plain")}
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/api/v1/analyses/", files=files, headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data["file_name"] == "test.txt"
    assert response_data["status"] == "PENDING"