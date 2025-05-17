import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import aiosmtplib
from app.services.email_service import send_verification_email
from app.services.auth_service import create_verification_token


@pytest.mark.integration
class TestEmailService:

    @patch("app.services.auth_service.create_verification_token")
    @patch("aiosmtplib.SMTP")
    async def test_send_verification_email_success(self, mock_smtp, mock_create_token):
        mock_create_token.return_value = "fake_token"

        mock_smtp_instance = AsyncMock()
        mock_smtp_context = MagicMock()
        mock_smtp_context.__aenter__.return_value = mock_smtp_instance
        mock_smtp.return_value = mock_smtp_context

        result = await send_verification_email("test@example.com", 1)

        assert result is True
        mock_create_token.assert_called_once_with(1)
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.send_message.assert_called_once()

    @patch("app.services.auth_service.create_verification_token")
    @patch("aiosmtplib.SMTP")
    async def test_send_verification_email_smtp_error(self, mock_smtp, mock_create_token):
        mock_create_token.return_value = "fake_token"

        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.login.side_effect = aiosmtplib.SMTPAuthenticationError(535, b"Authentication failed")

        mock_smtp_context = MagicMock()
        mock_smtp_context.__aenter__.return_value = mock_smtp_instance
        mock_smtp.return_value = mock_smtp_context

        result = await send_verification_email("test@example.com", 1)

        assert result is False

    @patch("app.services.auth_service.create_verification_token")
    @patch("aiosmtplib.SMTP")
    async def test_send_verification_email_general_error(self, mock_smtp, mock_create_token):
        mock_create_token.return_value = "fake_token"

        mock_smtp.side_effect = Exception("Unexpected error")

        result = await send_verification_email("test@example.com", 1)

        assert result is False

    def test_verification_token_creation(self):
        token = create_verification_token(123)

        assert isinstance(token, str)
        assert len(token) > 0
