from datetime import datetime
import psycopg2
import csv

DB_NAME = "credit_approval"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432" 

CUSTOMER_DATA_PATH = r"credit_approvel\utility\customer_data.csv"
LOAN_DATA_PATH = r"credit_approvel\utility\loan_data.csv"


# Function for Reading Customer data
def import_customer_data_from_csv():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        with open(CUSTOMER_DATA_PATH, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)

            for row in csv_reader:
                sql = """
                    INSERT INTO public.firstapp_customer 
                        (first_name, last_name, age, phone_number, monthly_salary, approved_limit)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (row[1], row[2], int(row[3]), int(row[4]), int(row[5]), int(row[6])))

       
        connection.commit()
        print("Customer data imported successfully from CSV into PostgreSQL.")

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        if connection:
            cursor.close()
            connection.close()


# Function for Reading Loan Data
def import_loan_data_from_csv():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()
        with open(LOAN_DATA_PATH, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                start_date = datetime.strptime(row[6], "%d-%m-%Y").date()
                end_date = datetime.strptime(row[7], "%d-%m-%Y").date()
                sql = """
                    INSERT INTO public.firstapp_loan 
                        (customer_info_id, loan_amount, tenure, interest_rate, monthly_payment, emi_paid_on_time, start_date, end_date)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (int(row[0]), int(row[1]), int(row[2]), float(row[3]), int(row[4]), int(row[5]), start_date, end_date))

        connection.commit()
        print("Loan data imported successfully from CSV into PostgreSQL.")

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        if connection:
            cursor.close()
            connection.close()



if __name__ == "__main__":
    import_customer_data_from_csv()
    import_loan_data_from_csv()


 