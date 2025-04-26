import os
import warnings
import torch
from typing import List, Dict, Any
import ssl
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

warnings.filterwarnings("ignore")

database_url = os.environ.get('DATABASE_URL')


class InsuranceRecommenderModel:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.insurances = []

        try:
            self._load_data_from_database()
        except Exception as e:
            print(f"Ошибка при загрузке данных из базы данных: {e}")
            self.insurances = []

        try:
            print(f"Пытаемся загрузить модель из {model_path}...")

            cache_dir = Path("/app/model_cache")
            cache_dir.mkdir(exist_ok=True)

            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            os.environ['TRANSFORMERS_OFFLINE'] = '0'

            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            ssl_context = ssl._create_unverified_context()
            ssl._create_default_https_context = lambda: ssl_context

            if model_path.startswith("sentence-transformers/"):
                try:
                    from sentence_transformers import SentenceTransformer
                    print("Загрузка модели с помощью SentenceTransformer...")

                    import huggingface_hub.constants
                    huggingface_hub.constants.HF_HUB_DISABLE_SYMLINKS_WARNING = True

                    self.model = SentenceTransformer(model_path, cache_folder=str(cache_dir),
                                                     use_auth_token=False)
                    print("Модель успешно загружена!")
                except Exception as e1:
                    print(f"Ошибка загрузки через SentenceTransformer: {e1}")
                    try:
                        from transformers import AutoModel, AutoTokenizer
                        print("Загрузка модели с помощью transformers...")

                        self.tokenizer = AutoTokenizer.from_pretrained(
                            model_path,
                            cache_dir=str(cache_dir),
                            local_files_only=False,
                            trust_remote_code=True,
                            use_auth_token=False,
                            proxies=None
                        )
                        self.model = AutoModel.from_pretrained(
                            model_path,
                            cache_dir=str(cache_dir),
                            local_files_only=False,
                            trust_remote_code=True,
                            use_auth_token=False,
                            proxies=None
                        ).to(self.device)
                        print("Модель успешно загружена!")
                    except Exception as e2:
                        print(f"Ошибка загрузки через transformers: {e2}")
                        raise
            else:
                try:
                    from transformers import AutoModel, AutoTokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
                    self.model = AutoModel.from_pretrained(model_path, local_files_only=True).to(self.device)
                except Exception as e:
                    print(f"Ошибка загрузки локальной модели: {e}")
                    raise
        except Exception as e:
            print(f"Общая ошибка при инициализации модели: {e}")
            raise

    def _load_data_from_database(self):
        """Загрузка страховых продуктов из базы данных PostgreSQL"""

        try:
            conn = psycopg2.connect(database_url)

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                with open('app/sql/get_insurances.sql', 'r') as sql_file:
                    sql_query = sql_file.read()

                cursor.execute(sql_query)
                self.insurances = cursor.fetchall()
                print(f"Загружено {len(self.insurances)} страховых полисов из базы данных")

            conn.close()
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            raise

    def _preprocess_user_data(self, user_data: Dict[str, Any]) -> str:
        profile = f"Возраст: {user_data['age']}, "
        profile += f"Пол: {user_data['gender']}, "
        profile += f"Профессия: {user_data['occupation']}, "
        profile += f"Доход: {user_data['income']}, "
        profile += f"Семейное положение: {user_data['marital_status']}, "
        profile += f"Есть дети: {'Да' if user_data['has_children'] else 'Нет'}, "
        profile += f"Владеет транспортным средством: {'Да' if user_data['has_vehicle'] else 'Нет'}, "
        profile += f"Владеет недвижимостью: {'Да' if user_data['has_home'] else 'Нет'}, "
        profile += f"Имеет медицинские проблемы: {'Да' if user_data['has_medical_conditions'] else 'Нет'}, "
        profile += f"Частота путешествий: {user_data['travel_frequency']}"
        return profile

    def _encode_text(self, text: str) -> torch.Tensor:
        """Кодирование текста в векторное представление"""
        try:
            if hasattr(self.model, 'encode'):
                return torch.tensor(self.model.encode([text]), device=self.device)
            else:
                inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self.model(**inputs)

                embeddings = outputs.last_hidden_state.mean(dim=1)
                return embeddings
        except Exception as e:
            print(f"Ошибка при кодировании текста: {e}")
            raise

    def _encode_insurance(self, insurance: Dict[str, Any]) -> torch.Tensor:
        insurance_text = f"Название: {insurance['product_name']}, "
        insurance_text += f"Категория: {insurance['category_name']}, "
        insurance_text += f"Описание: {insurance['description']}, "
        insurance_text += f"Премия: {insurance['premium']}, "
        insurance_text += f"Покрытие: {insurance['coverage']}, "
        insurance_text += f"Длительность: {insurance['duration']}"

        return self._encode_text(insurance_text)

    def _calculate_match_score(self, user_embedding: torch.Tensor, insurance_embedding: torch.Tensor) -> float:
        user_norm = user_embedding / user_embedding.norm(dim=1, keepdim=True)
        insurance_norm = insurance_embedding / insurance_embedding.norm(dim=1, keepdim=True)

        cos_sim = torch.sum(user_norm * insurance_norm, dim=1)
        score = (cos_sim + 1) / 2

        return float(score.item())

    def _generate_recommendation_reason(self, user_data: Dict[str, Any], insurance: Dict[str, Any],
                                        score: float) -> str:
        reasons = []

        if insurance['category_name'] == 'Медицинское страхование' and user_data['has_medical_conditions']:
            reasons.append(
                "учитывая ваши медицинские условия, этот полис медицинского страхования предоставит оптимальное покрытие")

        if insurance['category_name'] == 'Автострахование' and user_data['has_vehicle']:
            reasons.append("как владельцу транспортного средства, этот полис предоставит вам необходимую защиту")

        if insurance['category_name'] == 'Страхование недвижимости' and user_data['has_home']:
            reasons.append("как владельцу недвижимости, этот полис защитит ваше имущество")

        if insurance['category_name'] == 'Страхование жизни' and (
                user_data['has_children'] or user_data['marital_status'] == 'married'):
            reasons.append("этот полис обеспечит финансовую защиту для вашей семьи")

        if insurance['category_name'] == 'Страхование путешествий' and user_data['travel_frequency'] in ['often',
                                                                                                         'very_often']:
            reasons.append("учитывая частоту ваших поездок, этот полис страхования путешествий обеспечит вам защиту")

        if float(insurance['premium']) <= user_data['income'] * 0.05:
            reasons.append("стоимость данного полиса соответствует вашему уровню дохода")

        if not reasons:
            reasons = [f"этот полис имеет высокий рейтинг соответствия ({score:.2f}) для вашего профиля"]

        return "Рекомендовано, потому что " + " и ".join(reasons) + "."

    def _estimate_price(self, user_data: Dict[str, Any], insurance: Dict[str, Any]) -> float:
        """Оценка стоимости страхового полиса"""
        base_price = float(insurance['premium'])

        age_factor = min(2.0, max(0.8, user_data['age'] / 40))
        income_factor = min(1.5, max(0.5, user_data['income'] / 50000))

        risk_factors = 1.0
        if user_data['has_medical_conditions']:
            risk_factors *= 1.2
        if user_data['has_children']:
            risk_factors *= 1.1

        estimated_price = base_price * age_factor * income_factor * risk_factors

        return min(base_price * 1.5, max(base_price * 0.7, estimated_price))

    def get_recommendations(self, user_data: Dict[str, Any], top_n: int = 5) -> List[Dict[str, Any]]:
        if not self.insurances:
            print("Предупреждение: список страховых полисов пуст, пытаемся обновить из базы данных")
            self._load_data_from_database()

            if not self.insurances:
                return []

        user_profile_text = self._preprocess_user_data(user_data)
        user_embedding = self._encode_text(user_profile_text)

        recommendations = []

        for insurance in self.insurances:
            insurance_embedding = self._encode_insurance(insurance)
            match_score = self._calculate_match_score(user_embedding, insurance_embedding)

            if match_score > 0.3:
                estimated_price = self._estimate_price(user_data, insurance)
                recommendation_reason = self._generate_recommendation_reason(
                    user_data, insurance, match_score)

                recommendation = dict(insurance)
                recommendation['match_score'] = match_score
                recommendation['estimated_price'] = estimated_price
                recommendation['recommendation_reason'] = recommendation_reason

                recommendations.append(recommendation)

        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:top_n]
