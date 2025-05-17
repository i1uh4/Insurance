import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
import httpx
from app.routers.recommendations import check_recommendation, get_recommendations
from app.models.recommendation_models import UserCheckInfo, InsuranceRecommendationRequest


class TestRecommendationsRoutes:
    """Тесты для маршрутов рекомендаций"""

    @pytest.mark.asyncio
    @patch('app.routers.recommendations.execute_sql_file')
    async def test_check_recommendation_success(self, mock_execute_sql_file):
        """Тест успешной отметки просмотра рекомендации"""
        
        mock_user_data = [{"id": 1, "email": "test@example.com"}]
        mock_execute_sql_file.return_value = mock_user_data

        
        request = UserCheckInfo(product_id=5, user_email="test@example.com")

        
        result = await check_recommendation(request)

        
        assert result.code == 0
        assert result.message == "Success"

        
        
        first_call_args = mock_execute_sql_file.call_args_list[0][0]
        assert first_call_args[0] == "users/get_user_by_email.sql"
        assert first_call_args[1] == {"email": "test@example.com"}

        
        second_call_args = mock_execute_sql_file.call_args_list[1][0]
        assert second_call_args[0] == "insurances/insert_product_view.sql"
        assert second_call_args[1] == {"user_id": 1, "product_id": 5}
        assert second_call_args[2] == False  

    @pytest.mark.asyncio
    @patch('app.routers.recommendations.execute_sql_file')
    async def test_check_recommendation_user_not_found(self, mock_execute_sql_file):
        """Тест отметки просмотра для несуществующего пользователя"""
        
        mock_execute_sql_file.return_value = []

        
        request = UserCheckInfo(product_id=5, user_email="nonexistent@example.com")

        
        with pytest.raises(HTTPException) as exc_info:
            await check_recommendation(request)

        
        assert exc_info.value.status_code == 404
        assert "User with this email not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('app.routers.recommendations.os.getenv')
    @patch('httpx.AsyncClient.post')
    async def test_get_recommendations_success(self, mock_post, mock_getenv):
        """Тест успешного получения рекомендаций"""
        
        mock_getenv.return_value = "http://recommendation-api.example.com/recommendations"

        
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = [
            {
                "product_id": 1,
                "product_name": "Term Life Insurance",
                "provider": "Insurance Co.",
                "category_name": "Life Insurance",
                "description": "Long term insurance",
                "premium": 5000.0,
                "coverage": 1000000.0,
                "duration": 120,
                "estimated_price": 5000.0,
                "match_score": 0.85,
                "recommendation_reason": "Based on your age and income",
                "features": ["Feature 1", "Feature 2"],
                "suitable_for": ["Young professionals"],
                "risks_covered": ["Death", "Terminal illness"]
            }
        ]

        
        mock_post.return_value.__aenter__.return_value = mock_response

        
        request = InsuranceRecommendationRequest(
            age=30,
            gender="male",
            occupation="Developer",
            income=75000.0,
            marital_status="single",
            has_children=False,
            has_vehicle=True,
            has_home=False,
            has_medical_conditions=False,
            travel_frequency="often"
        )

        
        result = await get_recommendations(request)

        
        assert len(result) == 1
        assert result[0]["product_id"] == 1
        assert result[0]["product_name"] == "Term Life Insurance"
        assert result[0]["match_score"] == 0.85

        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://recommendation-api.example.com/recommendations"

    @pytest.mark.asyncio
    @patch('app.routers.recommendations.os.getenv')
    async def test_get_recommendations_missing_env_var(self, mock_getenv):
        """Тест случая, когда отсутствует переменная окружения с URL API"""
        
        mock_getenv.return_value = None

        
        request = InsuranceRecommendationRequest(
            age=30,
            gender="male",
            occupation="Developer",
            income=75000.0,
            marital_status="single",
            has_children=False,
            has_vehicle=True,
            has_home=False,
            has_medical_conditions=False,
            travel_frequency="often"
        )

        
        with pytest.raises(HTTPException) as exc_info:
            await get_recommendations(request)

        
        assert exc_info.value.status_code == 500
        assert "RECOMMENDATION_API_URL environment variable is not set" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('app.routers.recommendations.os.getenv')
    @patch('httpx.AsyncClient.post')
    async def test_get_recommendations_api_error(self, mock_post, mock_getenv):
        """Тест обработки ошибки от внешнего API"""
        
        mock_getenv.return_value = "http://recommendation-api.example.com/recommendations"

        
        http_error = httpx.HTTPStatusError(
            "API error",
            request=MagicMock(),
            response=MagicMock(status_code=502)
        )
        mock_post.return_value.__aenter__.side_effect = http_error

        
        request = InsuranceRecommendationRequest(
            age=30,
            gender="male",
            occupation="Developer",
            income=75000.0,
            marital_status="single",
            has_children=False,
            has_vehicle=True,
            has_home=False,
            has_medical_conditions=False,
            travel_frequency="often"
        )

        
        with pytest.raises(HTTPException) as exc_info:
            await get_recommendations(request)

        
        assert exc_info.value.status_code == 502
        assert "Error communicating with recommendation system" in str(exc_info.value.detail)
