from celery import shared_task
import pandas as pd
from datetime import datetime
from customers.models import Customer
from loans.models import Loan

def emi(P, annual_rate, n):
    r = (annual_rate/12)/100.0
    if n <= 0:
        return round(P, 2)
    if r == 0:
        return round(P/n, 2)
    return round(P * r * (1+r)**n / ((1+r)**n - 1), 2)

@shared_task
def ingest_excel(customers_path="data/customer_data.xlsx", loans_path="data/loan_data.xlsx"):
    cdf = pd.read_excel(customers_path)
    ldf = pd.read_excel(loans_path)
    # normalize columns
    norm = lambda df: df.rename(columns=lambda c: c.strip().lower().replace(" ", "_"))
    cdf, ldf = norm(cdf), norm(ldf)

    # map customer columns
    cdf["current_debt"] = cdf.get("current_debt", 0)
    for _, r in cdf.iterrows():
        Customer.objects.update_or_create(
            id=int(r.get("customer_id")),
            defaults=dict(
                first_name=str(r.get("first_name","")),
                last_name=str(r.get("last_name","")),
                phone_number=str(r.get("phone_number","")),
                age=int(r.get("age")) if pd.notna(r.get("age")) else None,
                monthly_salary=int(r.get("monthly_salary",0)),
                approved_limit=int(r.get("approved_limit",0)),
                current_debt=float(r.get("current_debt",0.0)),
            )
        )

    # normalize loan date columns that may differ
    if "date_of_approval" in ldf.columns and "start_date" not in ldf.columns:
        ldf = ldf.rename(columns={"date_of_approval":"start_date"})
    if "end_date_of_loan" in ldf.columns and "end_date" not in ldf.columns:
        ldf = ldf.rename(columns={"end_date_of_loan":"end_date"})

    # parse dates
    for col in ("start_date","end_date"):
        if col in ldf.columns:
            ldf[col] = pd.to_datetime(ldf[col], errors="coerce")

    # upsert loans
    for _, r in ldf.iterrows():
        amount = float(r.get("loan_amount", 0) or 0)
        tenure = int(r.get("tenure", 0) or 0)
        rate = float(r.get("interest_rate", 0) or 0)
        monthly = r.get("monthly_repayment_emi") or r.get("monthly_installment")
        if monthly is None or pd.isna(monthly):
            monthly = emi(amount, rate, tenure)
        Loan.objects.update_or_create(
            id=int(r.get("loan_id")) if pd.notna(r.get("loan_id")) else None,
            defaults=dict(
                customer_id=int(r.get("customer_id")),
                loan_amount=amount,
                tenure=tenure,
                interest_rate=rate,
                monthly_installment=float(monthly),
                emis_paid_on_time=int(r.get("emis_paid_on_time", 0) or 0),
                start_date=r.get("start_date").date() if pd.notna(r.get("start_date")) else None,
                end_date=r.get("end_date").date() if pd.notna(r.get("end_date")) else None,
            )
        )