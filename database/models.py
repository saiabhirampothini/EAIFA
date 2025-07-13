from sqlalchemy import Column, String, Integer, Float, Text
from sqlalchemy.dialects.sqlite import JSON
from database.base import Base
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime


class UserLoan(Base):
    __tablename__ = "user_loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    name = Column(String)
    age = Column(Integer)
    city = Column(String)
    country = Column(String)
    monthly_income = Column(Float)
    credit_score_now = Column(Integer)
    score_trend_12m = Column(Text)  # store as JSON string
    score_factors_12m = Column(Text)  # store as JSON string

    loan_id = Column(String)
    loan_type = Column(String)
    bank_name = Column(String)
    loan_amount = Column(Float)
    term_months = Column(Integer)
    int_rate = Column(Float)
    emi = Column(Float)
    dti = Column(Float)
    status = Column(String)
    start_date = Column(String)
    end_date = Column(String)



class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message_type = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
