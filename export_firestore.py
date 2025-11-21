# export_firestore.py
"""
Export Firestore collections to local JSON files.
Supports Emulator when FIRESTORE_EMULATOR_HOST is set, otherwise uses service account.

Usage:
    python export_firestore.py
Outputs:
    outputs/raw_json/recipes.json
    outputs/raw_json/users.json
    outputs/raw_json/interactions.json
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from datetime import datetime

OUT_DIR = "outputs/raw_json"
os.makedirs(OUT_DIR, exist_ok=True)

# Init Firebase admin client:
def init_firestore_client():
    # If emulator env var is set, use default initialize (no credentials) so admin SDK targets emulator
    emulator = os.environ.get("FIRESTORE_EMULATOR_HOST")
    if emulator:
        # When using emulator, initialize app without credentials
        firebase_admin.initialize_app()
        print(f"Using Firestore emulator at {emulator}")
    else:
        key_path = "serviceAccountKey.json"
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"serviceAccountKey.json not found at {key_path}. For production export, place the key in project root.")
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        print("Initialized Firestore admin with service account")

init_firestore_client()
db = firestore.client()

def doc_to_jsonable(d: DocumentSnapshot):
    """Convert firestore DocumentSnapshot.to_dict() to JSON serializable dict"""
    data = d.to_dict() or {}
    # convert timestamps to ISO strings
    for k, v in list(data.items()):
        # google.protobuf.Timestamp -> datetime
        try:
            if hasattr(v, "isoformat"):
                data[k] = v.isoformat()
        except Exception:
            # fallback: leave as-is
            pass
    data["_id"] = d.id
    return data

def export_collection(name: str):
    docs = db.collection(name).stream()
    items = []
    for d in docs:
        items.append(doc_to_jsonable(d))
    out_path = os.path.join(OUT_DIR, f"{name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(items)} documents -> {out_path}")

if __name__ == "__main__":
    for col in ["recipes", "users", "interactions"]:
        export_collection(col)
