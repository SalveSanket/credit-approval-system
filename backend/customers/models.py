from django.db import models

class Customer(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20, unique=True)
    age = models.IntegerField(null=True, blank=True)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField(default=0)
    current_debt = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.first_name} {self.last_name}"