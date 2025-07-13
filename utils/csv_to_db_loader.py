import pandas as pd
import json
from database.session import engine, SessionLocal
from database.models import UserLoan
from database.base import Base

def load_data():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    df = pd.read_csv("data/uk_credit_dataset.csv")
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    for _, row in df.iterrows():
        loan = UserLoan(
            user_id=row["user_id"],
            name=row["name"],
            age=row["age"],
            city=row["city"],
            country=row["country"],
            monthly_income=row["monthly_income"],
            credit_score_now=row["credit_score_now"],
            score_trend_12m=json.dumps(eval(row["score_trend_12m"])),
            score_factors_12m=json.dumps(eval(row["score_factors_12m"])),
            loan_id=row["loan_id"],
            loan_type=row["loan_type"],
            bank_name=row["bank_name"],
            loan_amount=row["loan_amount"],
            term_months=row["term_months"],
            int_rate=row["int_rate"],
            emi=row["emi"],
            dti=row["dti"],
            status=row["status"],
            start_date=row["start_date"],
            end_date=row["end_date"] if pd.notna(row["end_date"]) else None
        )
        session.add(loan)

    session.commit()
    session.close()

if __name__ == "__main__":
    load_data()
