from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
from .models import Customer, Loan
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json



# Register the new Customer View
@method_decorator(csrf_exempt, name='dispatch')
class RegisterCustomerView(View):
    def post(self, request):
        content_type = request.content_type

        if content_type != 'application/json':
            return JsonResponse({'error': 'Unsupported content type'}, status=415)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        age = data.get('age')
        monthly_income = data.get('monthly_income')
        phone_number = data.get('phone_number')

        if not all([first_name, last_name, age, monthly_income, phone_number]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            age = int(age)
            monthly_income = int(monthly_income)
            phone_number = int(phone_number)
        except ValueError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)

        approved_limit = round(36 * monthly_income, -5) 

        response_data = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            age=age,
            monthly_salary=monthly_income,
            phone_number=phone_number,
            approved_limit=approved_limit
        )

        # print("response_data: ", response_data.id)

        data['customer_id'] = response_data.id
        data['approval_limit'] = response_data.approved_limit
        return JsonResponse({'data': data}, status=201)


#Checking Loan Eligibility View
@method_decorator(csrf_exempt, name='dispatch')
class CheckLoanEligibilityView(View):
    def post(self, request):
        content_type = request.content_type
        if content_type != 'application/json':
            return JsonResponse({'error': 'Unsupported content type'}, status=415)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        customer_id = data.get('customer_id')
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        loan_data_query = Loan.objects.filter(customer_info_id=customer_id)
        credit_score = calculate_credit_score(loan_data_query, customer.approved_limit)
        #print("credit_score: ", credit_score)

        current_emis = get_current_emis(loan_data_query)
        approval_data= approve_loan(credit_score, interest_rate, customer.monthly_salary, current_emis)

        response_data = {
            'customer_id': customer_id,
            'approval': approval_data['approval'],
            'interest_rate': interest_rate,
            'tenure': tenure
        }
        if approval_data['approval']:
            monthly_installment = calculate_monthly_installment(loan_amount, interest_rate, tenure)
            response_data['monthly_installment'] = monthly_installment
            response_data['corrected_interest_rate'] = approval_data['interest_rate']
        else:
            response_data['message'] = approval_data['message']

        return JsonResponse(response_data)
    

# View Loan Deatils by loan id
@method_decorator(csrf_exempt, name='dispatch')
class ViewLoanDetailsByLoanIdView(View):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.select_related('customer_info').get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return JsonResponse({'error': 'Loan not found'}, status=404)

        try:
            customer = Customer.objects.get(id=loan.customer_info_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        loan_data = {
            'loan_id': loan.loan_id,
            'customer': {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone_number': customer.phone_number,
                'age': customer.age,
            },
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_payment,
            'tenure': loan.tenure,
        }

        return JsonResponse(loan_data)


# View for number loans per a particular customer
@method_decorator(csrf_exempt, name='dispatch')
class ViewLoanDetailsByCustomerIdView(View):
    def get(self, request, customer_id): 
        loan_data_query = Loan.objects.filter(customer_info_id=customer_id)
        if len(loan_data_query) == 0:
            return JsonResponse({'error': 'No Loans found for the provided customer id'}, status=404)
        loan_data_list = []
        for loan_data in loan_data_query:
            current_loan_info = {
                "loan_id": loan_data.loan_id,
                "loan_amount": loan_data.loan_amount,
                "interest_rate": loan_data.interest_rate,
                "monthly_installment": loan_data.monthly_payment,
                "repayments_left": loan_data.tenure - loan_data.emi_paid_on_time
            }
            loan_data_list.append(current_loan_info)

        return JsonResponse(loan_data_list, safe= False)


# View for a creating a new loan
@method_decorator(csrf_exempt, name='dispatch')
class CreateLoanView(View):
    LOAN_ELIGIBILITY_ENDPOINT = 'http://127.0.0.1:8000/api/v1/eligibility'
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        customer_id = data.get('customer_id')
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))

        if not all([customer_id, loan_amount, interest_rate, tenure]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)

        response = requests.post(self.LOAN_ELIGIBILITY_ENDPOINT, json={
            'customer_id': customer_id,
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'tenure': tenure
        })
        if response.status_code == 200:
            loan_eligibility_data = response.json()
            if loan_eligibility_data['approval']:
                print(loan_eligibility_data)
                loan = Loan.objects.create(customer_info=customer, loan_amount=loan_amount, interest_rate=interest_rate, tenure=tenure, monthly_payment=loan_eligibility_data['monthly_installment'], emi_paid_on_time=0, start_date=datetime.now().date(), end_date=datetime.now().date() + relativedelta(months=tenure))
                return JsonResponse({
                    'loan_id': loan.loan_id,
                    'customer_id': customer_id,
                    'loan_approved': True,
                    'monthly_installment': loan_eligibility_data['monthly_installment']
                })
            else:
                return JsonResponse({
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': loan_eligibility_data['message']
                })
        else:
            return JsonResponse({'error': 'Failed to check loan eligibility'}, status=response.status_code)

def get_current_emis(loan_data_query):
    current_emis = 0
    for loan in loan_data_query:
        end_date = datetime.strptime(str(loan.end_date), '%Y-%m-%d').date() 
        current_date = datetime.now().date()
        print(end_date, current_date)
        if end_date >= current_date:
            current_emis += loan.monthly_payment
    return current_emis

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    r = interest_rate / 12 / 100
    n = tenure
    monthly_installment = loan_amount * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return round(monthly_installment)

def calculate_credit_score(loan_data_query, approved_limit):
    paid_on_time_score = 0
    approved_volume_score = 0
    total_tenure = 0

    for loan in loan_data_query:
        paid_on_time_score += loan.emi_paid_on_time
        total_tenure += loan.tenure
        approved_volume_score += loan.loan_amount

    if approved_volume_score > approved_limit:
        return 0

    credit_score = (paid_on_time_score / total_tenure) * 100
        
    return round(credit_score)

def approve_loan(credit_rating, interest_rate, monthly_salary, current_emis):
    if credit_rating > 50:
        return {
            "approval": True, 
            "interest_rate": interest_rate
        }
    elif 30 < credit_rating <= 50:
        if interest_rate > 12:
            return {
                "approval": True, 
                "interest_rate": interest_rate
            }
        else:
            return {
                "approval": False, 
                "message":  "Interest rate must be greater than 12%"
            }
    elif 10 < credit_rating <= 30:
        if interest_rate > 16:
            return {
                "approval": True, 
                "interest_rate": interest_rate
            }
        else:
            return {
                "approval": False, 
                "message":  "Interest rate must be greater than 16%"
            }
    elif credit_rating <= 10:
        return {
            "approval": False, 
            "message":  "Credit rating too low, loan not approved"
        }
    
    if current_emis > 0.5 * monthly_salary:
        return {
            "approval": False, 
            "message":  "Sum of current EMIs exceeds 50% of monthly salary, loan not approved"
        }
    
    return {
            "approval": False, 
            "message":  "Loan not approved"
        }
