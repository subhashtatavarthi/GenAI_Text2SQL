import requests
import json

URL = "http://localhost:8000/api/v1/get-schema"

def test_sqlite():
    print("\n--- Testing SQLite Schema ---")
    payload = {
        "type": "sqlite",
        "dataset_id": "ds_sqlite_001",
        "details": {
            "file_path": "sales.db"
        }
    }
    try:
        res = requests.post(URL, json=payload)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(json.dumps(res.json(), indent=2))
        else:
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

def test_postgres():
    print("\n--- Testing Postgres Schema ---")
    payload = {
        "type": "postgres",
        "dataset_id": "ds_pg_001",
        "details": {
            "host": "localhost",
            "port": 5432,
            "database": "sales_db",
            "username": "postgres",
            "password": "password",
            "table_name": "sales_data" 
        }
    }
    try:
        res = requests.post(URL, json=payload)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(json.dumps(res.json(), indent=2))
        else:
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sqlite()
    test_postgres()
