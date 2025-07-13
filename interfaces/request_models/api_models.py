from pydantic import BaseModel
class EligibilityRequest(BaseModel):
    user_id: str
    loan_type: str
    loan_amount: float
    interest_rate: float
    loan_months: int
    current_income:int


class ChatQuery(BaseModel):
    query: str
