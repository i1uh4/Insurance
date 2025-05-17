import pytest
from app.services.auth_service import create_verification_token


@pytest.mark.integration
class TestEmailService:

    def test_verification_token_creation(self):
        token = create_verification_token(123)

        assert isinstance(token, str)
        assert len(token) > 0
