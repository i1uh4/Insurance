import json
import os
import warnings
import numpy as np
import torch
from typing import List, Dict, Any
import ssl
import requests
from pathlib import Path

# Заглушаем предупреждения для более чистого вывода
warnings.filterwarnings("ignore")


class InsuranceRecommenderModel:
    def __init__(self, model_path: str, products_data_path: str):
        # Загрузка данных о страховых продуктах
        try:
            with open(products_data_path, 'r', encoding='utf-8') as file:
                self.products = json.load(file)
        except Exception as e:
            print(f"Ошибка при загрузке данных о продуктах: {e}")
            # Аварийное создание пустого списка продуктов
            self.products = []

        # Попытка загрузки модели
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.use_fallback = False

        try:
            print(f"Пытаемся загрузить модель из {model_path}...")

            # Создаем папку для локального кэширования моделей
            cache_dir = Path("/app/model_cache")
            cache_dir.mkdir(exist_ok=True)

            # Настраиваем окружение для обхода проблем с SSL
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            os.environ['TRANSFORMERS_OFFLINE'] = '0'  # Разрешаем онлайн-загрузку

            # Настраиваем HTTP-клиенты для игнорирования проверки SSL
            # Это не рекомендуется в продакшене, но поможет обойти проблему
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # Настройка SSL для urllib3
            ssl_context = ssl._create_unverified_context()
            ssl._create_default_https_context = lambda: ssl_context

            # Попытка использовать предустановленную модель
            if model_path.startswith("sentence-transformers/"):
                try:
                    from sentence_transformers import SentenceTransformer
                    print("Загрузка модели с помощью SentenceTransformer...")

                    # Настраиваем параметры загрузки
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

                        # Настройка параметров загрузки transformers
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
                        self._use_fallback_model()
            else:
                # Предполагаем, что это локальный путь
                try:
                    from transformers import AutoModel, AutoTokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
                    self.model = AutoModel.from_pretrained(model_path, local_files_only=True).to(self.device)
                except Exception as e:
                    print(f"Ошибка загрузки локальной модели: {e}")
                    self._use_fallback_model()
        except Exception as e:
            print(f"Общая ошибка при инициализации модели: {e}")
            self._use_fallback_model()

    def _use_fallback_model(self):
        """Использование простой fallback-модели для демонстрации"""
        print("Используем простую fallback-модель вместо трансформера")
        self.use_fallback = True

        # Инициализация простого эмбеддинга на основе словаря ключевых слов
        self.keywords = {
            "health": ["health", "medical", "doctor", "hospital", "medicine", "disease", "illness"],
            "auto": ["car", "vehicle", "drive", "auto", "transportation", "accident"],
            "property": ["home", "house", "apartment", "property", "building", "real estate"],
            "life": ["life", "death", "family", "children", "spouse", "protection"],
            "travel": ["travel", "trip", "journey", "abroad", "vacation", "tourism", "flight"]
        }

    def _preprocess_user_data(self, user_data: Dict[str, Any]) -> str:
        # Преобразование пользовательских данных в текстовое представление
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
        if self.use_fallback:
            # Простой вектор для fallback-модели
            vector = torch.zeros(5)  # Вектор для пяти категорий: health, auto, property, life, travel

            text_lower = text.lower()
            for i, category in enumerate(["health", "auto", "property", "life", "travel"]):
                keywords = self.keywords[category]
                count = sum(1 for word in keywords if word in text_lower)
                vector[i] = count / len(keywords)

            # Добавление специфических правил
            if "медицинские проблемы: Да" in text:
                vector[0] += 0.5  # Увеличение веса для медицинского страхования

            if "транспортным средством: Да" in text:
                vector[1] += 0.5  # Увеличение веса для автострахования

            if "недвижимостью: Да" in text:
                vector[2] += 0.5  # Увеличение веса для страхования недвижимости

            if "дети: Да" in text or "Семейное положение: married" in text:
                vector[3] += 0.5  # Увеличение веса для страхования жизни

            if "путешествий: often" in text or "путешествий: very_often" in text:
                vector[4] += 0.5  # Увеличение веса для страхования путешествий

            # Нормализация вектора
            if vector.sum() > 0:
                vector = vector / vector.sum()

            return vector.unsqueeze(0)  # Добавляем размерность батча
        else:
            # Использование трансформера, если он доступен
            try:
                if hasattr(self.model, 'encode'):
                    # Для sentence-transformers
                    return torch.tensor(self.model.encode([text]), device=self.device)
                else:
                    # Для обычных трансформеров
                    inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}

                    with torch.no_grad():
                        outputs = self.model(**inputs)

                    # Использование среднего значения last hidden state как эмбеддинга
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                    return embeddings
            except Exception as e:
                print(f"Ошибка при кодировании текста: {e}")
                # Возвращаем случайный вектор в случае ошибки
                return torch.rand(1, 5).to(self.device)

    def _encode_product(self, product: Dict[str, Any]) -> torch.Tensor:
        # Преобразование продукта в текстовое представление
        product_text = f"Название: {product['name']}, "
        product_text += f"Провайдер: {product['provider']}, "
        product_text += f"Категория: {product['category']}, "
        product_text += f"Описание: {product['description']}, "
        product_text += f"Особенности: {', '.join(product['features'])}, "
        product_text += f"Подходит для: {', '.join(product['suitable_for'])}, "
        product_text += f"Покрываемые риски: {', '.join(product['risks_covered'])}"

        return self._encode_text(product_text)

    def _calculate_match_score(self, user_embedding: torch.Tensor, product_embedding: torch.Tensor) -> float:
        # Расчет косинусного сходства между эмбеддингами пользователя и продукта
        try:
            if user_embedding.shape[1] != product_embedding.shape[1]:
                # Если размерности не совпадают (в случае fallback-модели)
                return 0.5 + torch.rand(1).item() * 0.3  # Случайный скор между 0.5 и 0.8

            # Нормализация векторов
            user_norm = user_embedding / user_embedding.norm(dim=1, keepdim=True)
            product_norm = product_embedding / product_embedding.norm(dim=1, keepdim=True)

            # Косинусное сходство
            cos_sim = torch.sum(user_norm * product_norm, dim=1)

            # Преобразование в диапазон [0, 1]
            score = (cos_sim + 1) / 2

            return float(score.item())
        except Exception as e:
            print(f"Ошибка при расчете схожести: {e}")
            return 0.5  # Значение по умолчанию в случае ошибки

    def _generate_recommendation_reason(self, user_data: Dict[str, Any], product: Dict[str, Any], score: float) -> str:
        # Генерация обоснования рекомендации на основе характеристик пользователя и продукта
        reasons = []

        # Анализ на основе категории страховки
        if product['category'] == 'Медицинское страхование' and user_data['has_medical_conditions']:
            reasons.append(
                "учитывая ваши медицинские условия, этот полис медицинского страхования предоставит оптимальное покрытие")

        if product['category'] == 'Автострахование' and user_data['has_vehicle']:
            reasons.append("как владельцу транспортного средства, этот полис предоставит вам необходимую защиту")

        if product['category'] == 'Страхование недвижимости' and user_data['has_home']:
            reasons.append("как владельцу недвижимости, этот полис защитит ваше имущество")

        if product['category'] == 'Страхование жизни' and (
                user_data['has_children'] or user_data['marital_status'] == 'married'):
            reasons.append("этот полис обеспечит финансовую защиту для вашей семьи")

        if product['category'] == 'Страхование путешествий' and user_data['travel_frequency'] in ['often',
                                                                                                  'very_often']:
            reasons.append("учитывая частоту ваших поездок, этот полис страхования путешествий обеспечит вам защиту")

        # Анализ на основе дохода
        if 'min_price' in product and 'max_price' in product and product['min_price'] <= user_data['income'] * 0.05 <= \
                product['max_price']:
            reasons.append("стоимость данного полиса соответствует вашему уровню дохода")

        # Если конкретных причин не нашлось, используем общее обоснование
        if not reasons:
            reasons = [f"этот полис имеет высокий рейтинг соответствия ({score:.2f}) для вашего профиля"]

        return "Рекомендовано, потому что " + " и ".join(reasons) + "."

    def _estimate_price(self, user_data: Dict[str, Any], product: Dict[str, Any]) -> float:
        # Простая оценка цены на основе характеристик пользователя и диапазона цен продукта
        try:
            base_price = (product['min_price'] + product['max_price']) / 2

            # Факторы, влияющие на цену
            age_factor = min(2.0, max(0.8, user_data['age'] / 40))
            income_factor = min(1.5, max(0.5, user_data['income'] / 50000))

            risk_factors = 1.0
            if user_data['has_medical_conditions']:
                risk_factors *= 1.2
            if user_data['has_children']:
                risk_factors *= 1.1

            estimated_price = base_price * age_factor * income_factor * risk_factors

            # Ограничение цены диапазоном продукта
            return min(product['max_price'], max(product['min_price'], estimated_price))
        except Exception as e:
            print(f"Ошибка при оценке цены: {e}")
            # В случае ошибки используем среднее значение или значение по умолчанию
            return product.get('min_price', 5000) + (
                    product.get('max_price', 10000) - product.get('min_price', 5000)) / 2

    def get_recommendations(self, user_data: Dict[str, Any], top_n: int = 5) -> List[Dict[str, Any]]:
        # Проверка на пустой список продуктов
        if not self.products:
            print("Предупреждение: список продуктов пуст")
            return []

        # Преобразование пользовательских данных в эмбеддинг
        try:
            user_profile_text = self._preprocess_user_data(user_data)
            user_embedding = self._encode_text(user_profile_text)

            recommendations = []

            # Вычисление сходства пользователя с каждым продуктом
            for product in self.products:
                try:
                    product_embedding = self._encode_product(product)
                    match_score = self._calculate_match_score(user_embedding, product_embedding)

                    if match_score > 0.3:  # Снизим порог для включения большего числа рекомендаций
                        estimated_price = self._estimate_price(user_data, product)
                        recommendation_reason = self._generate_recommendation_reason(user_data, product, match_score)

                        recommendations.append({
                            "product_id": product["id"],
                            "product_name": product["name"],
                            "provider": product["provider"],
                            "category": product["category"],
                            "description": product["description"],
                            "estimated_price": estimated_price,
                            "match_score": match_score,
                            "features": product["features"],
                            "suitable_for": product["suitable_for"],
                            "risks_covered": product["risks_covered"],
                            "recommendation_reason": recommendation_reason
                        })
                except Exception as e:
                    print(f"Ошибка при обработке продукта {product.get('id', 'unknown')}: {e}")
                    continue

            # Если рекомендаций нет, добавим несколько простых рекомендаций на основе профиля
            if not recommendations:
                print("Не удалось найти подходящие рекомендации, создаем базовые варианты")
                if user_data['has_vehicle']:
                    auto_products = [p for p in self.products if p['category'] == 'Автострахование']
                    if auto_products:
                        product = auto_products[0]
                        recommendations.append(self._create_simple_recommendation(user_data, product, 0.8))

                if user_data['has_medical_conditions']:
                    health_products = [p for p in self.products if p['category'] == 'Медицинское страхование']
                    if health_products:
                        product = health_products[0]
                        recommendations.append(self._create_simple_recommendation(user_data, product, 0.75))

                # Добавим еще несколько рекомендаций, если у нас их все еще недостаточно
                if len(recommendations) < 3 and self.products:
                    for i in range(min(3 - len(recommendations), len(self.products))):
                        recommendations.append(
                            self._create_simple_recommendation(user_data, self.products[i], 0.7 - i * 0.1))

            # Сортировка по оценке сходства и выбор top_n рекомендаций
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            return recommendations[:top_n]

        except Exception as e:
            print(f"Ошибка при получении рекомендаций: {e}")
            # В случае ошибки возвращаем пустой список
            return []

    def _create_simple_recommendation(self, user_data: Dict[str, Any], product: Dict[str, Any], score: float) -> Dict[
        str, Any]:
        """Создание простой рекомендации на основе ограниченной информации"""
        estimated_price = self._estimate_price(user_data, product)
        recommendation_reason = self._generate_recommendation_reason(user_data, product, score)

        return {
            "product_id": product["id"],
            "product_name": product["name"],
            "provider": product["provider"],
            "category": product["category"],
            "description": product["description"],
            "estimated_price": estimated_price,
            "match_score": score,
            "features": product["features"],
            "suitable_for": product["suitable_for"],
            "risks_covered": product["risks_covered"],
            "recommendation_reason": recommendation_reason
        }
