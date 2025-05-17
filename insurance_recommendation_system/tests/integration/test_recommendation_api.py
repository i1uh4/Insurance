import pytest
from unittest.mock import patch, AsyncMock
import httpx
from fastapi import HTTPException
from app.models.recommendation_models import (
    InsuranceRecommendationRequest,
    UserCheckInfo,
    RecommendationWithInsurance
)


@pytest.mark.integration
class TestRecommendationAPI:

    @patch("httpx.AsyncClient.post")
    async def test_get_recommendations_success(self, mock_post, client, recommendation_request, mock_insurance_data):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_insurance_data
        mock_post.return_value = mock_response

        response = await client.post(
            "/recommendation/get_recommendations",
            json=recommendation_request
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(mock_insurance_data)

        assert data[0]["product_id"] == mock_insurance_data[0]["product_id"]
        assert data[0]["product_name"] == mock_insurance_data[0]["product_name"]
        assert data[0]["match_score"] == mock_insurance_data[0]["match_score"]

    @patch("httpx.AsyncClient.post")
    async def test_get_recommendations_external_api_error(self, mock_post, client, recommendation_request):
        mock_post.side_effect = httpx.HTTPStatusError(
            "API error",
            request=AsyncMock(),
            response=AsyncMock(status_code=502)
        )

        response = await client.post(
            "/recommendation/get_recommendations",
            json=recommendation_request
        )

        assert response.status_code == 502
        data = response.json()
        assert "detail" in data
        assert "recommendation system" in data["detail"].lower()

    @patch("httpx.AsyncClient.post")
    async def test_get_recommendations_unexpected_error(self, mock_post, client, recommendation_request):
        mock_post.side_effect = Exception("Unexpected error")

        response = await client.post(
            "/recommendation/get_recommendations",
            json=recommendation_request
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"].lower()

    @patch("app.database.execute_sql_file")
    async def test_check_recommendation_success(self, mock_execute_sql, client):
        mock_execute_sql.side_effect = [
            [{"id": 1, "email": "test@example.com"}],
            None
        ]

        check_data = {
            "product_id": 1,
            "user_email": "test@example.com"
        }

        response = await client.post(
            "/recommendation/check_recommendation",
            json=check_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "Success"

        mock_execute_sql.assert_any_call(
            "users/get_user_by_email.sql",
            {"email": "test@example.com"},
            read_only=False
        )
        mock_execute_sql.assert_any_call(
            "insurances/insert_product_view.sql",
            {"user_id": 1, "product_id": 1},
            read_only=False
        )

    @patch("app.database.execute_sql_file")
    async def test_check_recommendation_user_not_found(self, mock_execute_sql, client):
        mock_execute_sql.return_value = []

        check_data = {
            "product_id": 1,
            "user_email": "nonexistent@example.com"
        }

        response = await client.post(
            "/recommendation/check_recommendation",
            json=check_data
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
