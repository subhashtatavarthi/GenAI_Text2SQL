import psycopg2
from psycopg2 import sql
import random
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Default to a local default if not provided, but mostly expect env inputs
# Format: postgresql://user:password@host:port/dbname
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "sales_db")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASS = os.getenv("PG_PASS", "postgres")

def get_connection(autocommit=True):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        conn.autocommit = autocommit
        return conn
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        return None

def generate_date():
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def get_quarter(month):
    if month <= 3: return "Q1"
    elif month <= 6: return "Q2"
    elif month <= 9: return "Q3"
    else: return "Q4"

def generate_data():
    conn = get_connection()
    if not conn:
        print("Could not connect to database. Please check your credentials.")
        print("You can set PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS environment variables.")
        sys.exit(1)

    cursor = conn.cursor()

    # Drop table if exists
    print("Dropping table if exists...")
    cursor.execute("DROP TABLE IF EXISTS sales_data;")

    # Create Table
    print("Creating table sales_data...")
    cursor.execute("""
    CREATE TABLE sales_data (
        id SERIAL PRIMARY KEY,
        org_name VARCHAR(100),
        product_name VARCHAR(100),
        sales_amount DECIMAL(15, 2),
        quantity INTEGER,
        sale_date DATE,
        year INTEGER,
        quarter VARCHAR(10),
        month VARCHAR(20),
        region VARCHAR(50)
    );
    """)

    orgs = ["Acme Corp", "Globex", "Soylent Corp", "Initech", "Umbrella Corp", "Stark Ind", "Wayne Ent", "Cyberdyne"]
    products = ["Laptop", "Mouse", "Monitor", "Keyboard", "Server", "License", "Support"]
    regions = ["North", "South", "East", "West"]

    print("Generating 10,000 records...")
    
    data = []
    for _ in range(10000):
        date = generate_date()
        year = date.year
        month_num = date.month
        month_name = date.strftime("%B")
        quarter = get_quarter(month_num)
        
        org = random.choice(orgs)
        product = random.choice(products)
        region = random.choice(regions)
        qty = random.randint(1, 50)
        price = random.randint(100, 5000)
        amount = qty * price
        
        data.append((org, product, amount, qty, date.strftime("%Y-%m-%d"), year, quarter, month_name, region))

    # Batch Insert
    args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s)", x).decode('utf-8') for x in data)
    cursor.execute("INSERT INTO sales_data (org_name, product_name, sales_amount, quantity, sale_date, year, quarter, month, region) VALUES " + args_str)

    print(f"Successfully inserted {len(data)} records.")
    
    # Verification
    cursor.execute("SELECT Count(*) FROM sales_data")
    count = cursor.fetchone()[0]
    print(f"Total Records in DB: {count}")
    
    conn.close()

if __name__ == "__main__":
    generate_data()
