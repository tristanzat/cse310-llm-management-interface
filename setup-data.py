import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def get_data_from_json(filename: str):
    try:
        with open(filename) as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error: {e}")
        exit


def main():
    firebase_admin.initialize_app(credentials.Certificate("admin-key.json"))

    db = firestore.client()

    chats = db.collection("chats")

    data = get_data_from_json("llm_requests_sample.json")

    for item in data:
        filtered = {k: v for k, v in item.items() if k != 'id'}
        filtered["timestamp"] = datetime.fromisoformat(filtered["timestamp"].replace("Z", "+00:00"))
        chats.document(item["id"]).set(filtered)

if __name__ == "__main__":
    main()