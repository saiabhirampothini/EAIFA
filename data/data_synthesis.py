
# import pandas as pd
# import random
# from faker import Faker
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta

# fake = Faker("en_GB")

# def generate_uk_credit_dataset_with_loans(lending_club_csv_path: str, sample_size: int = 1000) -> pd.DataFrame:
#     # Load Lending Club data
#     df = pd.read_csv(lending_club_csv_path, low_memory=False)
    
#     selected_columns = [
#         'loan_amnt', 'term', 'int_rate', 'installment',
#         'annual_inc', 'purpose', 'dti',
#         'fico_range_low', 'fico_range_high'
#     ]
#     df = df[selected_columns].dropna().sample(n=sample_size, random_state=42).reset_index(drop=True)

#     # Transformations
#     df['term_months'] = df['term'].str.extract(r'(\d+)').astype(int)
#     df['loan_amount'] = (df['loan_amnt'] * 0.78).round(2)
#     df['emi'] = (df['installment'] * 0.78).round(2)
#     df['monthly_income'] = (df['annual_inc'] / 12 * 0.78).round(2)

#     df['credit_score_now'] = ((df['fico_range_low'] + df['fico_range_high']) / 2).apply(
#         lambda x: int((x - 300) / 550 * 999)
#     )

#     def simulate_score_trend(current_score):
#         return [max(300, min(999, current_score + random.randint(-25, 25))) for _ in range(12)]
    
#     df['score_trend_12m'] = df['credit_score_now'].apply(simulate_score_trend)

#     # Loan type mapping
#     df['loan_type'] = df['purpose'].map({
#         'car': 'car',
#         'credit_card': 'credit_card',
#         'home_improvement': 'home',
#         'debt_consolidation': 'personal',
#         'major_purchase': 'personal',
#         'medical': 'personal',
#         'moving': 'personal',
#         'vacation': 'personal',
#         'house': 'home',
#         'wedding': 'personal',
#         'small_business': 'business'
#     }).fillna('personal')

#     # Bank name by loan type
#     bank_options = {
#         'car': ['Barclays', 'Tesco Bank', 'NatWest', 'Halifax'],
#         'credit_card': ['HSBC', 'Lloyds', 'NatWest'],
#         'home': ['Lloyds', 'Santander', 'Halifax', 'Barclays'],
#         'personal': ['HSBC', 'Monzo', 'Starling', 'Barclays'],
#         'business': ['HSBC', 'Barclays', 'Santander']
#     }
#     df['bank_name'] = df['loan_type'].apply(lambda lt: random.choice(bank_options.get(lt, ['Barclays'])))

#     # Assign users (repeat some)
#     df['user_id'] = [f"user_{i % (sample_size // 2)}" for i in range(sample_size)]
#     df['name'] = [fake.name() for _ in range(sample_size)]
#     df['age'] = [random.randint(22, 65) for _ in range(sample_size)]
#     df['city'] = [fake.city() for _ in range(sample_size)]
#     df['country'] = 'UK'

#     # Loan ID
#     df['loan_id'] = [f"loan_{uid}_{random.randint(1000, 9999)}" for uid in df['user_id']]

#     # Loan start date (within last 3 years)
#     df['start_date_obj'] = [
#         (datetime.today() - timedelta(days=random.randint(30, 1095))).replace(day=1)
#         for _ in range(sample_size)
#     ]

#     # Loan status
#     df['status'] = [random.choice(['Current', 'Fully Paid', 'Default', 'Late']) for _ in range(sample_size)]

#     # Calculate end date
#     df['end_date'] = df.apply(
#         lambda row: (row['start_date_obj'] + relativedelta(months=int(row['term_months']))).strftime('%Y-%m')
#         if row['status'] in ['Fully Paid', 'Default'] else None,
#         axis=1
#     )
#     df['start_date'] = df['start_date_obj'].dt.strftime('%Y-%m')

#     # Final columns
#     final_columns = [
#         'user_id', 'name', 'age', 'city', 'country',
#         'monthly_income', 'credit_score_now', 'score_trend_12m',
#         'loan_id', 'loan_type', 'bank_name',
#         'loan_amount', 'term_months', 'int_rate', 'emi', 'dti',
#         'status', 'start_date', 'end_date'
#     ]

#     return df[final_columns]

import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

fake = Faker("en_GB")

def generate_uk_credit_dataset_with_score_factors(lending_club_csv_path: str, sample_size: int = 1000) -> pd.DataFrame:
    # Load Lending Club data
    df = pd.read_csv(lending_club_csv_path, low_memory=False)
    
    selected_columns = [
        'loan_amnt', 'term', 'int_rate', 'installment',
        'annual_inc', 'purpose', 'dti',
        'fico_range_low', 'fico_range_high'
    ]
    df = df[selected_columns].dropna().sample(n=sample_size, random_state=42).reset_index(drop=True)

    # Transform values to UK-style
    df['term_months'] = df['term'].str.extract(r'(\d+)').astype(int)
    df['loan_amount'] = (df['loan_amnt'] * 0.78).round(2)
    df['emi'] = (df['installment'] * 0.78).round(2)
    df['monthly_income'] = (df['annual_inc'] / 12 * 0.78).round(2)

    df['credit_score_now'] = ((df['fico_range_low'] + df['fico_range_high']) / 2).apply(
        lambda x: int((x - 300) / 550 * 999)
    )

    # Simulate 12-month credit score trend
    def simulate_score_trend(current_score):
        return [max(300, min(999, current_score + random.randint(-25, 25))) for _ in range(12)]
    df['score_trend_12m'] = df['credit_score_now'].apply(simulate_score_trend)

    # Define pool of score-affecting behaviors
    credit_factors_pool = [
        "High credit utilization",
        "On-time payment",
        "Late payment",
        "New credit card opened",
        "Credit card closed",
        "Loan account closed",
        "Credit limit increased",
        "Missed EMI payment",
        "Too many recent inquiries",
        "No recent activity",
        "Positive repayment history",
        "Account age improved"
    ]

    # Generate list of month labels
    def generate_last_12_months():
        base = datetime.today().replace(day=1)
        return [(base - relativedelta(months=i)).strftime('%Y-%m') for i in range(12)][::-1]
    
    months_list = generate_last_12_months()

    # Simulate monthly score factor logs
    def simulate_factors_12m():
        return [
            {
                "month": month,
                "factors": random.sample(credit_factors_pool, random.randint(1, 2))
            }
            for month in months_list
        ]
    df['score_factors_12m'] = [simulate_factors_12m() for _ in range(len(df))]

    # Loan type mapping
    df['loan_type'] = df['purpose'].map({
        'car': 'car',
        'credit_card': 'credit_card',
        'home_improvement': 'home',
        'debt_consolidation': 'personal',
        'major_purchase': 'personal',
        'medical': 'personal',
        'moving': 'personal',
        'vacation': 'personal',
        'house': 'home',
        'wedding': 'personal',
        'small_business': 'business'
    }).fillna('personal')

    # Assign bank names based on loan type
    bank_options = {
        'car': ['Barclays', 'Tesco Bank', 'NatWest', 'Halifax'],
        'credit_card': ['HSBC', 'Lloyds', 'NatWest'],
        'home': ['Lloyds', 'Santander', 'Halifax', 'Barclays'],
        'personal': ['HSBC', 'Monzo', 'Starling', 'Barclays'],
        'business': ['HSBC', 'Barclays', 'Santander']
    }
    df['bank_name'] = df['loan_type'].apply(lambda lt: random.choice(bank_options.get(lt, ['Barclays'])))

    # Assign user info (repeat users)
    df['user_id'] = [f"user_{i % (sample_size // 2)}" for i in range(sample_size)]
    df['name'] = [fake.name() for _ in range(sample_size)]
    df['age'] = [random.randint(22, 65) for _ in range(sample_size)]
    df['city'] = [fake.city() for _ in range(sample_size)]
    df['country'] = 'UK'

    # Unique loan ID
    df['loan_id'] = [f"loan_{uid}_{random.randint(1000, 9999)}" for uid in df['user_id']]

    # Loan start date (within past 3 years)
    df['start_date_obj'] = [
        (datetime.today() - timedelta(days=random.randint(30, 1095))).replace(day=1)
        for _ in range(sample_size)
    ]

    # Status and conditional end date
    df['status'] = [random.choice(['Current', 'Fully Paid', 'Default', 'Late']) for _ in range(sample_size)]
    df['end_date'] = df.apply(
        lambda row: (row['start_date_obj'] + relativedelta(months=int(row['term_months']))).strftime('%Y-%m')
        if row['status'] in ['Fully Paid', 'Default'] else None,
        axis=1
    )
    df['start_date'] = df['start_date_obj'].dt.strftime('%Y-%m')

    # Final fields
    final_columns = [
        'user_id', 'name', 'age', 'city', 'country',
        'monthly_income', 'credit_score_now', 'score_trend_12m', 'score_factors_12m',
        'loan_id', 'loan_type', 'bank_name',
        'loan_amount', 'term_months', 'int_rate', 'emi', 'dti',
        'status', 'start_date', 'end_date'
    ]

    return df[final_columns]
