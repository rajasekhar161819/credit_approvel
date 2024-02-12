from django.db import models
from django.utils import timezone

# Create your models here.

class Customer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    monthly_salary = models.IntegerField(default=0)
    approved_limit = models.IntegerField(default=0)

    def __int__(self):
        return self.id 
    
class Loan(models.Model):
    customer_info = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id = models.AutoField(primary_key=True, unique=True)
    loan_amount = models.IntegerField(default=0)
    tenure = models.IntegerField(default=0)
    interest_rate = models.FloatField(default=0)
    monthly_payment = models.IntegerField(default=0)
    emi_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True,default=timezone.now)
    end_date = models.DateField(null=True, blank=True, default=timezone.now)

    def __int__(self):
        return self.loan_id
    
