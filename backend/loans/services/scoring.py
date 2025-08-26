from datetime import date
from django.db.models import Sum, Count
from customers.models import Customer
from loans.models import Loan

def _current_loans_qs(loans_qs):
    today = date.today()
    return loans_qs.filter(end_date__isnull=True) | loans_qs.filter(end_date__gte=today)

def compute_credit_score(customer: Customer) -> int:
    loans_qs = Loan.objects.filter(customer=customer)
    # Hard rule: if current loan amount sum > approved_limit → 0
    curr_amt = _current_loans_qs(loans_qs).aggregate(Sum("loan_amount"))["loan_amount__sum"] or 0
    if curr_amt > customer.approved_limit:
        return 0

    total_loans = loans_qs.count()
    # rough on-time ratio: paid_on_time over (12 * number_of_loans)
    denom = max(1, total_loans * 12)
    on_time = loans_qs.aggregate(Sum("emis_paid_on_time"))["emis_paid_on_time__sum"] or 0
    on_time_ratio = max(0.0, min(1.0, on_time / denom))
    on_time_score = on_time_ratio * 100 * 0.35

    past_loans_score = (1 - 1 / (1 + total_loans)) * 100 * 0.15

    this_year = date.today().year
    started_this_year = loans_qs.filter(start_date__year=this_year).aggregate(Count("id"))["id__count"] or 0
    current_year_score = (50 if started_this_year > 0 else 100) * 0.15

    total_volume = loans_qs.aggregate(Sum("loan_amount"))["loan_amount__sum"] or 0
    # penalty grows with volume relative to limit
    volume_penalty = min(100, (total_volume / (customer.approved_limit + 1)) * 50)
    volume_score = max(0, 100 - volume_penalty) * 0.15

    score = on_time_score + past_loans_score + current_year_score + volume_score
    return int(round(max(0, min(100, score))))