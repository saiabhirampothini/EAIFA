class Loan:
    def __init__(
        self,
        loan_id: str,
        loan_type: str,
        bank_name: str,
        loan_amount: float,
        term_months: int,
        int_rate: float,
        emi: float,
        dti: float,
        status: str,
        start_date: str,
        end_date: str
    ):
        self.loan_id = loan_id
        self.loan_type = loan_type
        self.bank_name = bank_name
        self.loan_amount = loan_amount
        self.term_months = term_months
        self.int_rate = int_rate
        self.emi = emi
        self.dti = dti
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
