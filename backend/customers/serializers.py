from rest_framework import serializers
from .models import Customer
from common.finance import round_to_nearest_lakh

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    age = serializers.IntegerField(min_value=18, max_value=100)
    monthly_income = serializers.IntegerField(min_value=1)
    phone_number = serializers.CharField()

    def create(self, validated_data):
        approved_limit = round_to_nearest_lakh(36 * validated_data["monthly_income"])
        cust = Customer.objects.create(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            age=validated_data["age"],
            monthly_salary=validated_data["monthly_income"],
            approved_limit=approved_limit,
            phone_number=validated_data["phone_number"],
            current_debt=0.0,
        )
        return cust

class RegisterResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    monthly_income = serializers.IntegerField(source="monthly_salary")

    class Meta:
        model = Customer
        fields = ("id","name","age","monthly_income","approved_limit","phone_number")

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"