import sys
import os

# Add project root to path so we can import src
sys.path.append(os.getcwd())

from src.database.sqlite import get_db

def test_app_connection():
    print("--- Testing App Database Connection ---")
    try:
        # 1. Initialize DB Connection using our src module
        db = get_db()
        print("✅ Successfully initialized SQLDatabase instance.")
        
        # 2. Check Dialect
        print(f"ℹ️  Dialect: {db.dialect}")
        
        # 3. Check Usable Tables (should match include_tables=['sales_data'])
        print(f"ℹ️  Usable Tables: {db.get_usable_table_names()}")
        
        # 4. Run a Query through the wrapper
        result = db.run("SELECT org_name, sales_amount FROM sales_data LIMIT 3")
        print(f"✅ Query Result Sample:\n{result}")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_app_connection()
