from rest_framework import serializers

class CheckEligibilityIn(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=1)
    interest_rate = serializers.FloatField(min_value=0)
    tenure = serializers.IntegerField(min_value=1)

class CheckEligibilityOut(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField(allow_null=True)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField(allow_null=True)
    reason = serializers.CharField()

class CreateLoanIn(CheckEligibilityIn):
    pass