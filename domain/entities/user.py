from typing import List, Dict, Optional
from domain.entities.loan import Loan

class User:
    def __init__(
        self,
        user_id: str,
        name: str,
        age: int,
        city: str,
        country: str,
        monthly_income: float,
        credit_score_now: int,
        score_trend_12m: Dict[str, int],
        score_factors_12m: Dict[str, float],
        loans: Optional[List[Loan]] = None
    ):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.city = city
        self.country = country
        self.monthly_income = monthly_income
        self.credit_score_now = credit_score_now
        self.score_trend_12m = score_trend_12m
        self.score_factors_12m = score_factors_12m
        self.loans = loans or []
