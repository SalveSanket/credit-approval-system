from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from customers.models import Customer
from .models import Loan
from .serializers import CheckEligibilityIn, CheckEligibilityOut, CreateLoanIn
from .services.scoring import compute_credit_score
from .services.eligibility import evaluate

@api_view(["POST"])
def check_eligibility(request):
    ser = CheckEligibilityIn(data=request.data)
    if not ser.is_valid():
        return Response({"errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
    d = ser.validated_data
    customer = get_object_or_404(Customer, id=d["customer_id"])

    score = compute_credit_score(customer)
    result = evaluate(customer, d["loan_amount"], d["interest_rate"], d["tenure"], score)

    out = {
        "customer_id": customer.id,
        "approval": result["approved"],
        "interest_rate": float(d["interest_rate"]),
        "corrected_interest_rate": (None if not result["approved"] else result["final_rate"])
            if result["approved"] and result["final_rate"] == d["interest_rate"] else result["final_rate"],
        "tenure": d["tenure"],
        "monthly_installment": result["emi"] if result["approved"] else None,
        "reason": result["reason"],
    }
    return Response(CheckEligibilityOut(out).data, status=status.HTTP_200_OK)

@api_view(["POST"])
def create_loan(request):
    ser = CreateLoanIn(data=request.data)
    if not ser.is_valid():
        return Response({"errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
    d = ser.validated_data
    customer = get_object_or_404(Customer, id=d["customer_id"])

    score = compute_credit_score(customer)
    result = evaluate(customer, d["loan_amount"], d["interest_rate"], d["tenure"], score)
    if not result["approved"]:
        return Response(
            {
                "loan_id": None,
                "customer_id": customer.id,
                "loan_approved": False,
                "message": result["reason"],
                "monthly_installment": result["emi"],
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # save loan with final rate & EMI
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=d["loan_amount"],
        tenure=d["tenure"],
        interest_rate=result["final_rate"],
        monthly_installment=result["emi"],
        emis_paid_on_time=0,
    )
    return Response(
        {
            "loan_id": loan.id,
            "customer_id": customer.id,
            "loan_approved": True,
            "message": "Loan created",
            "monthly_installment": loan.monthly_installment,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
def view_loan(request, loan_id: int):
    loan = get_object_or_404(Loan, id=loan_id)
    c = loan.customer
    return Response(
        {
            "loan_id": loan.id,
            "customer": {
                "id": c.id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "phone_number": c.phone_number,
                "age": c.age,
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure,
            "start_date": loan.start_date,
            "end_date": loan.end_date,
        }
    )

@api_view(["GET"])
def view_loans(request, customer_id: int):
    from datetime import date
    loans = Loan.objects.filter(customer_id=customer_id)
    today = date.today()
    items = []
    for ln in loans:
        # months left (rough): if end_date present
        if ln.end_date:
            months_left = (ln.end_date.year - today.year) * 12 + (ln.end_date.month - today.month)
            months_left = max(0, months_left)
        else:
            months_left = ln.tenure  # fallback
        items.append({
            "loan_id": ln.id,
            "loan_amount": ln.loan_amount,
            "interest_rate": ln.interest_rate,
            "monthly_installment": ln.monthly_installment,
            "repayments_left": months_left
        })
    return Response(items)