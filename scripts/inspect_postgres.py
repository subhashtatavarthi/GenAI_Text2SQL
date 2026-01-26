import psycopg2
import os
from tabulate import tabulate

# Default credentials matching docker-compose
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "sales_db")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASS = os.getenv("PG_PASS", "password")

def inspect_postgres():
    print("--- Inspecting PostgreSQL Database ---")
    print(f"Connecting to {DB_NAME} at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        
        # 1. Total Count
        cursor.execute("SELECT COUNT(*) FROM sales_data")
        count = cursor.fetchone()[0]
        print(f"\n[Total Records]: {count}")

        # 2. Sample Data
        print("\n[Sample Data - Top 5]")
        cursor.execute("SELECT id, org_name, product_name, sales_amount, sale_date, region FROM sales_data LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            headers = ["ID", "Org", "Product", "Amount", "Date", "Region"]
            print(tabulate(rows, headers=headers, tablefmt="psql"))
        else:
            print("No data found.")

        conn.close()
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("\nTroubleshooting:")
        print("1. Is the Docker container running? (run 'docker-compose ps')")
        print("2. Did you run 'scripts/generate_data_pg.py' to seed the data?")
        print("3. Check your credentials in .env or script defaults.")

if __name__ == "__main__":
    inspect_postgres()
