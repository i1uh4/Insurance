import os
import torch
import random
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

database_url = os.environ.get('DATABASE_URL')


class InsuranceRecommenderModel:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.insurances = []

        try:
            self._load_data_from_database()
        except Exception as e:
            print(f"Error loading data from database: {e}")
            self.insurances = []

        try:
            print(f"Loading DialoGPT model from {model_path}...")

            print("Loading tokenizer... ", end="", flush=True)
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                padding_side='left',
                use_fast=True
            )

            print("Loading model... ", end="", flush=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map=self.device,
                low_cpu_mem_usage=True
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            print("DialoGPT model successfully loaded!")
        except Exception as e:
            print(f"Error loading DialoGPT model: {e}")
            raise

    def _load_data_from_database(self):
        try:
            conn = psycopg2.connect(database_url)

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                with open('app/sql/get_insurances.sql', 'r') as sql_file:
                    sql_query = sql_file.read()

                cursor.execute(sql_query)
                self.insurances = cursor.fetchall()
                print(f"Loaded {len(self.insurances)} insurance policies from database")

            conn.close()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def _generate_text(self, prompt: str, max_length: int = 100) -> str:
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = inputs.to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2
                )

            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = generated_text[len(prompt):].strip()

            if not response:
                return "Подходящий продукт для ваших потребностей"

            sentences = response.split('.')
            clean_response = sentences[0].strip() if sentences else response

            return clean_response[:200] if len(clean_response) > 200 else clean_response

        except Exception as e:
            print(f"Error generating text: {e}")
            return "Рекомендуемый страховой продукт"

    def _format_user_profile(self, user_data: Dict[str, Any]) -> str:
        profile = f"Пользователь {user_data['age']} лет, {user_data['gender']}, работает в сфере {user_data['occupation']}. "
        profile += f"Годовой доход: {user_data['income']} рублей. "

        if user_data['marital_status'] == 'married':
            profile += "Состоит в браке. "
        elif user_data['marital_status'] == 'single':
            profile += "Не состоит в браке. "

        if user_data['has_children']:
            profile += "Имеет детей. "

        if user_data['has_vehicle']:
            profile += "Владеет автомобилем. "

        if user_data['has_home']:
            profile += "Владеет недвижимостью. "

        if user_data['has_medical_conditions']:
            profile += "Имеет проблемы со здоровьем. "

        travel_map = {
            'very_often': 'Очень часто путешествует',
            'often': 'Часто путешествует',
            'sometimes': 'Иногда путешествует',
            'rarely': 'Редко путешествует'
        }
        profile += travel_map.get(user_data['travel_frequency'], 'Практически не путешествует') + "."

        return profile

    def _format_insurance_info(self, insurance: Dict[str, Any]) -> str:
        info = f"Страховой продукт: {insurance['product_name']} от компании {insurance['provider']}. "
        info += f"Категория: {insurance['category_name']}. "

        if insurance['description']:
            info += f"Описание: {insurance['description']} "

        info += f"Стоимость: {float(insurance['premium']):.2f} рублей. "
        info += f"Покрытие: {float(insurance['coverage']):.2f} рублей."

        return info

    def _calculate_similarity_score(self, user_profile: str, insurance_info: str) -> float:
        user_tokens = set(user_profile.lower().split())
        insurance_tokens = set(insurance_info.lower().split())

        intersection = len(user_tokens.intersection(insurance_tokens))
        union = len(user_tokens.union(insurance_tokens))

        if union == 0:
            return 0.3

        base_score = intersection / union
        category_bonus = 0.0

        if any(word in insurance_info.lower() for word in ['медицинское', 'здоровье']):
            category_bonus += 0.1
        if any(word in insurance_info.lower() for word in ['авто', 'транспорт']):
            category_bonus += 0.05
        if any(word in insurance_info.lower() for word in ['недвижимость', 'дом']):
            category_bonus += 0.05

        final_score = min(0.95, base_score + category_bonus + random.uniform(0.1, 0.3))
        return max(0.3, final_score)

    def _generate_recommendation_reason(self, user_data: Dict[str, Any], insurance: Dict[str, Any]) -> str:
        prompt = f"Объясни почему страховой продукт {insurance['product_name']} категории {insurance['category_name']} подходит пользователю {user_data['age']} лет с доходом {user_data['income']} рублей:"
        return self._generate_text(prompt, max_length=80)

    def _generate_features(self, insurance: Dict[str, Any]) -> List[str]:
        features = []
        for i in range(4):
            prompt = f"Назови одну ключевую особенность страхового продукта {insurance['category_name']} номер {i + 1}:"
            feature = self._generate_text(prompt, max_length=30)
            if feature and len(feature) > 5:
                features.append(feature)
        return features

    def _generate_suitable_for(self, insurance: Dict[str, Any]) -> List[str]:
        suitable = []
        for i in range(3):
            prompt = f"Для кого подходит {insurance['category_name']} вариант {i + 1}:"
            target = self._generate_text(prompt, max_length=25)
            if target and len(target) > 5:
                suitable.append(target)
        return suitable

    def _generate_risks_covered(self, insurance: Dict[str, Any]) -> List[str]:
        risks = []
        for i in range(5):
            prompt = f"Какой риск покрывает {insurance['category_name']} пункт {i + 1}:"
            risk = self._generate_text(prompt, max_length=25)
            if risk and len(risk) > 5:
                risks.append(risk)
        return risks

    def _estimate_price(self, user_data: Dict[str, Any], insurance: Dict[str, Any]) -> float:
        base_price = float(insurance['premium'])

        age_factor = 1.0
        if user_data['age'] < 25:
            age_factor = 1.3
        elif user_data['age'] > 65:
            age_factor = 1.4
        elif user_data['age'] > 50:
            age_factor = 1.2

        income_factor = 1.0
        if user_data['income'] > 2000000:
            income_factor = 0.9
        elif user_data['income'] > 1000000:
            income_factor = 0.95

        risk_factor = 1.0
        if user_data['has_medical_conditions'] and insurance['category_name'] == 'Медицинское страхование':
            risk_factor *= 1.3
        if user_data['has_children']:
            risk_factor *= 1.1

        random_factor = 1.0 + (random.random() * 0.1 - 0.05)
        estimated_price = base_price * age_factor * income_factor * risk_factor * random_factor

        return min(base_price * 2.0, max(base_price * 0.7, estimated_price))

    def get_recommendations(self, user_data: Dict[str, Any], top_n: int = 10) -> List[Dict[str, Any]]:
        if not self.insurances:
            print("Warning: Insurance list is empty, trying to update from database")
            self._load_data_from_database()

            if not self.insurances:
                return []

        user_profile = self._format_user_profile(user_data)
        recommendations = []

        for insurance in self.insurances:
            try:
                insurance_info = self._format_insurance_info(insurance)
                match_score = self._calculate_similarity_score(user_profile, insurance_info)

                if match_score > 0.3:
                    recommendation_reason = self._generate_recommendation_reason(user_data, insurance)
                    estimated_price = self._estimate_price(user_data, insurance)
                    features = self._generate_features(insurance)
                    suitable_for = self._generate_suitable_for(insurance)
                    risks_covered = self._generate_risks_covered(insurance)

                    recommendation = dict(insurance)
                    recommendation['match_score'] = match_score
                    recommendation['estimated_price'] = estimated_price
                    recommendation['recommendation_reason'] = recommendation_reason
                    recommendation['features'] = features
                    recommendation['suitable_for'] = suitable_for
                    recommendation['risks_covered'] = risks_covered

                    recommendations.append(recommendation)
            except Exception as e:
                print(f"Error processing insurance {insurance.get('product_id', 'unknown')}: {e}")
                continue

        recommendations = sorted(recommendations, key=lambda x: x["match_score"], reverse=True)

        final_recommendations = []
        categories_added = set()

        for rec in recommendations:
            category = rec["category_name"]
            if category not in categories_added and len(final_recommendations) < top_n:
                final_recommendations.append(rec)
                categories_added.add(category)

        remaining_slots = top_n - len(final_recommendations)
        if remaining_slots > 0:
            remaining_recs = [r for r in recommendations if r not in final_recommendations]
            final_recommendations.extend(remaining_recs[:remaining_slots])

        print(f"Generated {len(final_recommendations)} recommendations")
        return final_recommendations
