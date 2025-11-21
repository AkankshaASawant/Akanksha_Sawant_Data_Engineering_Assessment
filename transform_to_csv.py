# transform_to_csv.py
"""
Transform raw JSON exports into normalized CSV tables:
 - recipes.csv
 - ingredients.csv
 - steps.csv
 - interactions.csv
 - users.csv

Usage:
    python transform_to_csv.py
Requires:
    outputs/raw_json/{recipes,users,interactions}.json
Outputs:
    outputs/csv/*.csv
"""
import os
import json
import pandas as pd

RAW_DIR = "outputs/raw_json"
OUT_DIR = "outputs/csv"
os.makedirs(OUT_DIR, exist_ok=True)

def load_json(fname):
    path = os.path.join(RAW_DIR, fname)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run export_firestore.py first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def transform_recipes():
    recipes = load_json("recipes.json")
    rec_rows = []
    ing_rows = []
    step_rows = []
    for r in recipes:
        rid = r.get("_id")
        # normalize tags to comma-separated string for recipes.csv
        tags = r.get("tags") or []
        if isinstance(tags, list):
            tags_str = ",".join([str(t) for t in tags])
        else:
            tags_str = str(tags) if tags else ""
        rec_rows.append({
            "recipe_id": rid,
            "title": r.get("title"),
            "description": r.get("description"),
            "prep_time_minutes": r.get("prep_time_minutes"),
            "cook_time_minutes": r.get("cook_time_minutes"),
            "difficulty": r.get("difficulty"),
            "servings": r.get("servings"),
            "tags": tags_str,
            "created_at": r.get("created_at")
        })
        # ingredients
        for idx, ing in enumerate(r.get("ingredients") or []):
            ing_rows.append({
                "recipe_id": rid,
                "ingredient_order": idx + 1,
                "name": ing.get("name"),
                "quantity": ing.get("quantity")
            })
        # steps
        for s in r.get("steps") or []:
            # some steps may be simple strings - handle both shapes
            if isinstance(s, dict):
                instruction = s.get("instruction") or s.get("text") or ""
                order = s.get("order") or None
            else:
                instruction = str(s)
                order = None
            step_rows.append({
                "recipe_id": rid,
                "step_order": order,
                "instruction": instruction
            })
    pd.DataFrame(rec_rows).to_csv(os.path.join(OUT_DIR, "recipes.csv"), index=False)
    pd.DataFrame(ing_rows).to_csv(os.path.join(OUT_DIR, "ingredients.csv"), index=False)
    pd.DataFrame(step_rows).to_csv(os.path.join(OUT_DIR, "steps.csv"), index=False)
    print("Wrote recipes.csv, ingredients.csv, steps.csv")

def transform_interactions():
    interactions = load_json("interactions.json")
    rows = []
    for it in interactions:
        rows.append({
            "interaction_id": it.get("_id"),
            "recipe_id": it.get("recipe_id"),
            "user_id": it.get("user_id"),
            "type": it.get("type"),
            "timestamp": it.get("timestamp"),
            "rating": it.get("rating")
        })
    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "interactions.csv"), index=False)
    print("Wrote interactions.csv")

def transform_users():
    users = load_json("users.json")
    rows = []
    for u in users:
        # Accept multiple possible field names from different seeders
        uid = u.get("_id") or u.get("user_id") or u.get("id")
        name = u.get("displayName") or u.get("name") or u.get("full_name")
        email = u.get("email")
        created_at = u.get("joined_at") or u.get("created_at") or u.get("joinedAt")
        rows.append({
            "user_id": uid,
            "name": name,
            "email": email,
            "created_at": created_at
        })
    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "users.csv"), index=False)
    print("Wrote users.csv")

if __name__ == "__main__":
    transform_recipes()
    transform_interactions()
    transform_users()
