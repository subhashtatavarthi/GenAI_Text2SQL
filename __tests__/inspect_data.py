import sqlite3
import os
from tabulate import tabulate # Optional, for pretty printing if installed, otherwise fallback

DB_PATH = "sales.db"

def inspect():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"--- Inspecting {DB_PATH} ---")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Get Schema
    print("\n[Schema]")
    cursor.execute("PRAGMA table_info(sales_data)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")

    # 2. Total Count
    cursor.execute("SELECT COUNT(*) FROM sales_data")
    count = cursor.fetchone()[0]
    print(f"\n[Total Records]: {count}")

    # 3. Sample Data
    print("\n[Sample Data - Top 5]")
    cursor.execute("SELECT * FROM sales_data LIMIT 5")
    rows = [dict(row) for row in cursor.fetchall()]
    
    if rows:
        header = rows[0].keys()
        data = [row.values() for row in rows]
        try:
            print(tabulate(data, headers=header, tablefmt="grid"))
        except ImportError:
            # Fallback if tabulate not installed
            print(f"{list(header)}")
            for row in data:
                print(row)

    # 4. Aggregation Test
    print("\n[Aggregation: Total Sales by Region]")
    cursor.execute("""
        SELECT region, SUM(sales_amount) as total_sales 
        FROM sales_data 
        GROUP BY region
    """)
    for row in cursor.fetchall():
        print(f"  {row['region']}: ${row['total_sales']:,.2f}")

    conn.close()

if __name__ == "__main__":
    inspect()
