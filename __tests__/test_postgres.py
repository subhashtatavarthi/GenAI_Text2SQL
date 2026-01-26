import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.getcwd())

# Mocking settings to avoid actually loading .env if it's not set up
# or we can just rely on the real env if the user sets it.
# For this verify script, we want to try the Real Connection.

class TestPostgresConnection(unittest.TestCase):
    
    def test_postgres_connection(self):
        print("\n--- Testing PostgreSQL Connection ---")
        try:
            from src.database.postgres import get_postgres_db
            
            # This calls the factory which tries to connect
            db = get_postgres_db()
            
            print("✅ Successfully initialized SQLDatabase instance for Postgres.")
            print(f"ℹ️  Dialect: {db.dialect}")
            
            tables = db.get_usable_table_names()
            print(f"ℹ️  Usable Tables: {tables}")
            
            if 'sales_data' not in tables:
                print("⚠️  Warning: 'sales_data' table not found. Did you run generate_data_pg.py?")
            else:
                result = db.run("SELECT org_name, sales_amount FROM sales_data LIMIT 3")
                print(f"✅ Query Result Sample:\n{result}")

        except Exception as e:
            print(f"❌ Postgres Connection Failed: {e}")
            # Fail the test but print the error
            self.fail(f"Connection failed: {e}")

if __name__ == "__main__":
    unittest.main()
