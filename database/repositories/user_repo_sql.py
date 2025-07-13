import json
from domain.entities.user import User
from domain.entities.loan import Loan
from domain.repositories.user_repo import UserRepository
from database.models import UserLoan
from sqlalchemy.orm import Session
from collections import defaultdict

class UserRepositorySQL(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str) -> User:
        records = self.db.query(UserLoan).filter(UserLoan.user_id == user_id).all()

        if not records:
            raise Exception("User not found")

        # First record contains user metadata
        first = records[0]

        loans = [
            Loan(
                loan_id=r.loan_id,
                loan_type=r.loan_type,
                bank_name=r.bank_name,
                loan_amount=r.loan_amount,
                term_months=r.term_months,
                int_rate=r.int_rate,
                emi=r.emi,
                dti=r.dti,
                status=r.status,
                start_date=r.start_date,
                end_date=r.end_date
            ) for r in records
        ]

        return User(
            user_id=first.user_id,
            name=first.name,
            age=first.age,
            city=first.city,
            country=first.country,
            monthly_income=first.monthly_income,
            credit_score_now=first.credit_score_now,
            score_trend_12m=json.loads(first.score_trend_12m),
            score_factors_12m=json.loads(first.score_factors_12m),
            loans=loans
        )


    def get_all_users_summary(self) -> str:
        # Fetch all loan records
        records = self.db.query(UserLoan).all()

        if not records:
            return "[]"

        user_summary = {}
        loan_counts = defaultdict(int)
        total_dti = defaultdict(float)

        for r in records:
            uid = r.user_id
            loan_counts[uid] += 1
            total_dti[uid] += r.dti if r.dti is not None else 0.0

            if uid not in user_summary:
                user_summary[uid] = {
                    "user_id": r.user_id,
                    "name": r.name,
                    "age": r.age,
                    "city": r.city,
                    "country": r.country,
                    "monthly_income": r.monthly_income,
                    "credit_score_now": r.credit_score_now,
                    "loan_count": 0,     # to be filled below
                    "dti": 0.0           # to be averaged below
                }

        # Finalize values
        for uid in user_summary:
            user_summary[uid]["loan_count"] = loan_counts[uid]
            user_summary[uid]["dti"] = round(total_dti[uid] / loan_counts[uid], 2)

        return json.dumps(list(user_summary.values()))
