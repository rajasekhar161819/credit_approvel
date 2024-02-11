from datetime import datetime
import psycopg2
import csv

# PostgreSQL database connection settings
DB_NAME = "credit_approval"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"  # Default PostgreSQL port

# CSV file path
CUSTOMER_DATA_PATH = r"credit_approvel\utility\customer_data.csv"
LOAN_DATA_PATH = r"credit_approvel\utility\loan_data.csv"

def import_customer_data_from_csv():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        # Open the CSV file
        with open(CUSTOMER_DATA_PATH, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Prepare the SQL INSERT statement
                sql = """
                    INSERT INTO public.firstapp_customer 
                        (id, first_name, last_name, age, phone_number, monthly_salary, approved_limit)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s)
                """
                # Execute the SQL statement
                cursor.execute(sql, (int(row[0]), row[1], row[2], int(row[3]), int(row[4]), int(row[5]), int(row[6])))

       
        # Commit the transaction
        connection.commit()
        print("Customer data imported successfully from CSV into PostgreSQL.")

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()



def import_loan_data_from_csv():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        # Open the CSV file
        with open(LOAN_DATA_PATH, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Prepare the SQL INSERT statement
                start_date = datetime.strptime(row[7], "%d-%m-%Y").date()
                end_date = datetime.strptime(row[8], "%d-%m-%Y").date()
                sql = """
                    INSERT INTO public.firstapp_loan 
                        (loan_id, customer_info_id, loan_amount, tenure, interest_rate, monthly_payment, emi_paid_on_time, start_date, end_date)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                # Execute the SQL statement
                cursor.execute(sql, (int(row[0]), int(row[1]), int(row[2]), int(row[3]), float(row[4]), int(row[5]), int(row[6]), start_date, end_date))

       
        # Commit the transaction
        connection.commit()
        print("Loan data imported successfully from CSV into PostgreSQL.")

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()



if __name__ == "__main__":
    import_customer_data_from_csv()
    import_loan_data_from_csv()


 