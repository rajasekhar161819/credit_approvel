from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit',) 

# class LoanSerializer(serializers.ModelSerializer):
#     customer_info = CustomerSerializer

#     class Meta:
#         model = Loan
#         fields = ('loan_id', 'customer_info', 'loan_amount', 'interest_rate', 'tenure', 'emi_paid_on_time', 'start_date', 'end_date')