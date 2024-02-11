from django.urls import path
from .views import RegisterCustomerView, CheckLoanEligibilityView, ViewLoanDetailsByLoanIdView, ViewLoanDetailsByCustomerIdView, CreateLoanView

urlpatterns = [
    path('register', RegisterCustomerView.as_view()),
    path('eligibility', CheckLoanEligibilityView.as_view()),
    path('view-loan/<int:loan_id>', ViewLoanDetailsByLoanIdView.as_view()),
    path('view-loans/<int:customer_id>', ViewLoanDetailsByCustomerIdView.as_view()),
    path('create-loan', CreateLoanView.as_view()),
    
    
 ]
