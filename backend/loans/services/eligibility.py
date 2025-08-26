from django.db.models import Sum
from customers.models import Customer
from loans.models import Loan
from .emi import monthly_emi

def slab_min_rate(score: int):
    if score > 50: return None
    if 30 < score <= 50: return 12.0
    if 10 < score <= 30: return 16.0
    return "REJECT"

def sum_current_emis(customer_id: int) -> float:
    from datetime import date
    today = date.today()
    qs = Loan.objects.filter(customer_id=customer_id)
    qs = qs.filter(end_date__isnull=True) | qs.filter(end_date__gte=today)
    return qs.aggregate(Sum("monthly_installment"))["monthly_installment__sum"] or 0.0

def evaluate(customer: Customer, loan_amount: float, interest_rate: float, tenure: int, score: int):
    # interest correction based on slab
    min_rate = slab_min_rate(score)
    if min_rate == "REJECT":
        return {"approved": False, "reason": "Credit score too low", "final_rate": None, "emi": None}

    final_rate = max(interest_rate, min_rate) if min_rate is not None else interest_rate
    emi = monthly_emi(loan_amount, final_rate, tenure)

    current_emi_sum = sum_current_emis(customer.id)
    can_afford = (current_emi_sum + emi) <= 0.5 * customer.monthly_salary
    if not can_afford:
        return {"approved": False, "reason": "EMIs exceed 50% of salary", "final_rate": final_rate, "emi": emi}

    return {"approved": True, "reason": "Eligible", "final_rate": final_rate, "emi": emi}