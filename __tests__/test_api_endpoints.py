import requests
import json
import unittest

BASE_URL = "http://localhost:8000/api/v1"

class TestAPIEndpoints(unittest.TestCase):
    
    # --- Schema Endpoint Tests ---
    
    def test_schema_sqlite(self):
        print("\n[TEST] Get Schema (SQLite)...")
        payload = {
            "type": "sqlite",
            "dataset_id": "test_ds_01",
            "details": {
                "file_path": "sales.db"
            }
        }
        response = requests.post(f"{BASE_URL}/get-schema", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"✅ Success. Tables found: {[t['table_name'] for t in data['tables']]}")
        self.assertTrue(len(data['tables']) > 0)
        self.assertEqual(data['database_type'], "sqlite")

    def test_schema_postgres(self):
        print("\n[TEST] Get Schema (Postgres)...")
        payload = {
            "type": "postgres",
            "dataset_id": "test_ds_02",
            "details": {
                "host": "localhost",
                "port": 5432,
                "database": "sales_db",
                "username": "postgres",
                "password": "password",
                "table_name": "sales_data" 
            }
        }
        # Note: This test assumes Docker Postgres is running
        try:
            response = requests.post(f"{BASE_URL}/get-schema", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success. Tables found: {[t['table_name'] for t in data['tables']]}")
            else:
                print(f"⚠️  Skipping (Postgres might be down/unreachable): {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
             print("⚠️  Skipping: Server not running or Postgres down.")

    # --- Query Endpoint Tests ---

    def test_query_openai(self):
        print("\n[TEST] Text-to-SQL (OpenAI)...")
        payload = {
            "question": "What is the total sales amount for 'Acme Corp'?",
            "model_provider": "openai"
        }
        
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SQL Generated: {data.get('sql_query')}")
            print(f"✅ Answer: {data.get('answer')}")
            self.assertEqual(data['provider'], "openai")
        else:
            print(f"❌ Failed: {response.text}")

    def test_query_gemini(self):
        print("\n[TEST] Text-to-SQL (Gemini)...")
        payload = {
            "question": "Show me top 3 products by quantity sales.",
            "model_provider": "gemini"
        }
        
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SQL Generated: {data.get('sql_query')}")
            print(f"✅ Answer: {data.get('answer')}")
            self.assertEqual(data['provider'], "gemini")
        else:
            print(f"❌ Failed (Expected if NO KEY): {response.text}")

if __name__ == "__main__":
    print("⚠️  Ensure the API server is running (uvicorn src.main:app) before running tests!")
    unittest.main()
