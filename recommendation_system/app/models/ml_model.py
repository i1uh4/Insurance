import os
import json
import torch
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from transformers import AutoTokenizer, AutoModel, pipeline

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
            print(f"Loading model from {model_path}...")

            
            if model_path.startswith("sentence-transformers/"):
                try:
                    from sentence_transformers import SentenceTransformer
                    print("Loading model using SentenceTransformer...")
                    self.model = SentenceTransformer(model_path)
                    self.use_sentence_transformer = True
                    print("Model successfully loaded!")
                except Exception as e:
                    print(f"Error loading through SentenceTransformer: {e}")
                    raise
            else:
                try:
                    
                    self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                    self.model = AutoModel.from_pretrained(model_path).to(self.device)
                    self.use_sentence_transformer = False
                    print("Model successfully loaded!")
                except Exception as e:
                    print(f"Error loading through transformers: {e}")
                    raise
        except Exception as e:
            print(f"General error during model initialization: {e}")
            raise

    def _load_data_from_database(self):
        """Load insurance products from PostgreSQL database"""
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

    def _encode_text(self, text: str) -> torch.Tensor:
        """Encode text to vector representation"""
        if self.use_sentence_transformer:
            return torch.tensor(self.model.encode([text])).to(self.device)
        else:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings

    def _format_user_profile(self, user_data: Dict[str, Any]) -> str:
        """Format user data into a rich profile description"""
        
        profile = f"A {user_data['age']}-year-old {user_data['gender']} working as {user_data['occupation']} "
        profile += f"with an annual income of ${user_data['income']}. "
        profile += f"Marital status: {user_data['marital_status']}. "

        if user_data['has_children']:
            profile += "Has children. "
        else:
            profile += "No children. "

        if user_data['has_vehicle']:
            profile += "Owns a vehicle. "
        else:
            profile += "Does not own a vehicle. "

        if user_data['has_home']:
            profile += "Owns a home. "
        else:
            profile += "Does not own a home. "

        if user_data['has_medical_conditions']:
            profile += "Has medical conditions. "
        else:
            profile += "No significant medical conditions. "

        profile += f"Travel frequency: {user_data['travel_frequency']}."

        return profile

    def _format_insurance_info(self, insurance: Dict[str, Any]) -> str:
        """Format insurance data into a rich description"""
        
        info = f"Insurance: {insurance['product_name']} by {insurance['provider']} "
        info += f"in the {insurance['category_name']} category. "
        info += f"{insurance['description']} "
        info += f"Premium: ${float(insurance['premium']):.2f}. "
        info += f"Coverage: ${float(insurance['coverage']):.2f}. "
        info += f"Duration: {insurance['duration']} months."

        return info

    def _calculate_match_score(self, user_embedding: torch.Tensor, insurance_embedding: torch.Tensor) -> float:
        """Calculate semantic similarity between user profile and insurance description"""
        
        user_norm = user_embedding / user_embedding.norm(dim=1, keepdim=True)
        insurance_norm = insurance_embedding / insurance_embedding.norm(dim=1, keepdim=True)

        
        cos_sim = torch.sum(user_norm * insurance_norm, dim=1)

        
        score = (cos_sim + 1) / 2

        return float(score.item())

    def _generate_recommendation_reason(self, user_data: Dict[str, Any], insurance: Dict[str, Any]) -> str:
        """Generate a detailed recommendation reason based on user profile and insurance details"""
        reasons = []

        
        if insurance['category_name'] == 'Медицинское страхование':
            if user_data['has_medical_conditions']:
                reasons.append(
                    "this health insurance policy offers comprehensive coverage for your existing medical conditions"
                )
            else:
                reasons.append(
                    "this health insurance policy provides preventive care and coverage in case of unexpected medical needs"
                )

        
        if insurance['category_name'] == 'Автострахование':
            if user_data['has_vehicle']:
                if user_data['income'] > 75000:
                    reasons.append(
                        "this premium auto insurance policy provides extensive coverage for your vehicle with additional benefits"
                    )
                else:
                    reasons.append(
                        "this auto insurance policy offers essential protection for your vehicle at an affordable price"
                    )

        
        if insurance['category_name'] == 'Страхование недвижимости':
            if user_data['has_home']:
                if user_data['has_children']:
                    reasons.append(
                        "this home insurance policy provides comprehensive coverage for your property and additional protection for families with children"
                    )
                else:
                    reasons.append(
                        "this home insurance policy offers tailored protection for your property"
                    )

        
        if insurance['category_name'] == 'Страхование жизни':
            if user_data['has_children'] or user_data['marital_status'] == 'married':
                reasons.append(
                    "this life insurance policy ensures financial security for your family in case of unforeseen circumstances"
                )
            else:
                reasons.append(
                    "this life insurance policy provides coverage that aligns with your individual needs"
                )

        
        if insurance['category_name'] == 'Страхование путешествий':
            if user_data['travel_frequency'] in ['often', 'very_often']:
                reasons.append(
                    "this travel insurance offers comprehensive protection during your frequent trips"
                )
            else:
                reasons.append(
                    "this travel insurance provides essential coverage for your occasional travel needs"
                )

        
        if user_data['age'] < 30:
            reasons.append(
                "this policy is designed with features beneficial for younger policyholders"
            )
        elif user_data['age'] >= 60:
            reasons.append(
                "this policy includes special provisions for senior clients"
            )

        
        if float(insurance['premium']) <= user_data['income'] * 0.01:
            reasons.append(
                "the premium for this policy fits comfortably within your budget"
            )

        
        if not reasons:
            reasons = ["this policy has a good match for your overall profile"]

        return "We recommend this policy because " + " and ".join(reasons) + "."

    def _estimate_price(self, user_data: Dict[str, Any], insurance: Dict[str, Any]) -> float:
        """Calculate personalized price estimate based on user profile and base premium"""
        base_price = float(insurance['premium'])

        
        age = user_data['age']
        if age < 25:
            age_factor = 1.3
        elif age > 65:
            age_factor = 1.4
        elif age > 50:
            age_factor = 1.2
        else:
            age_factor = 1.0

        
        income = user_data['income']
        if income > 100000:
            income_factor = 0.9
        elif income > 50000:
            income_factor = 0.95
        else:
            income_factor = 1.0

        
        risk_factor = 1.0

        if user_data['has_medical_conditions'] and insurance['category_name'] == 'Медицинское страхование':
            risk_factor *= 1.3

        if user_data['has_children']:
            risk_factor *= 1.1

        
        if insurance['category_name'] == 'Автострахование' and user_data['has_vehicle']:
            risk_factor *= 1.0

        if insurance['category_name'] == 'Страхование недвижимости' and user_data['has_home']:
            risk_factor *= 1.0

        if insurance['category_name'] == 'Страхование путешествий':
            if user_data['travel_frequency'] == 'very_often':
                risk_factor *= 1.4
            elif user_data['travel_frequency'] == 'often':
                risk_factor *= 1.2

        
        estimated_price = base_price * age_factor * income_factor * risk_factor

        
        return min(base_price * 2.0, max(base_price * 0.7, estimated_price))

    def get_recommendations(self, user_data: Dict[str, Any], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get personalized insurance recommendations for a user"""
        if not self.insurances:
            print("Warning: Insurance list is empty, trying to update from database")
            self._load_data_from_database()

            if not self.insurances:
                return []

        user_profile = self._format_user_profile(user_data)
        user_embedding = self._encode_text(user_profile)

        recommendations = []

        for insurance in self.insurances:
            try:
                insurance_info = self._format_insurance_info(insurance)
                insurance_embedding = self._encode_text(insurance_info)

                match_score = self._calculate_match_score(user_embedding, insurance_embedding)

                if match_score > 0.3:
                    recommendation_reason = self._generate_recommendation_reason(user_data, insurance)

                    estimated_price = self._estimate_price(user_data, insurance)

                    recommendation = dict(insurance)
                    recommendation['match_score'] = match_score
                    recommendation['estimated_price'] = estimated_price
                    recommendation['recommendation_reason'] = recommendation_reason

                    recommendations.append(recommendation)
            except Exception as e:
                print(f"Error processing insurance {insurance.get('product_id', 'unknown')}: {e}")
                continue

        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        return recommendations[:top_n]
