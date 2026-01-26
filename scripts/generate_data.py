import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = "sales.db"

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
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Table
    cursor.execute("""
    CREATE TABLE sales_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_name TEXT,
        product_name TEXT,
        sales_amount REAL,
        quantity INTEGER,
        sale_date DATE,
        year INTEGER,
        quarter TEXT,
        month TEXT,
        region TEXT
    )
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

    cursor.executemany("""
        INSERT INTO sales_data (org_name, product_name, sales_amount, quantity, sale_date, year, quarter, month, region)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    print(f"Successfully inserted {len(data)} records.")
    
    # Verification
    cursor.execute("SELECT Count(*) FROM sales_data")
    count = cursor.fetchone()[0]
    print(f"Total Records in DB: {count}")
    
    conn.close()

if __name__ == "__main__":
    generate_data()
