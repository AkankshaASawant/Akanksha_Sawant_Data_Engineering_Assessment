# validate.py
"""
Validate datasets and write a validation report:
 - outputs/reports/validation_report.json (detailed)
 - outputs/reports/validation_summary.csv (tabular summary)
Rules:
 - recipes: required fields, numeric non-negative times, difficulty in {easy,medium,hard}, non-empty arrays
 - interactions: required fields, type in allowed set
 - users: required fields, simple email check
Usage:
    python validate.py
"""
import json
import os
import csv
from datetime import datetime

RAW_DIR = "outputs/raw_json"
REPORT_DIR = "outputs/reports"
os.makedirs(REPORT_DIR, exist_ok=True)

VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_INTERACTION_TYPES = {"view", "like", "cook_attempt"}

def load(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run export_firestore.py first.")
    return json.load(open(path, "r", encoding="utf-8"))

# ---------- Recipes ----------
def validate_recipes():
    items = load(os.path.join(RAW_DIR, "recipes.json"))
    valid = []
    invalid = []
    for r in items:
        reasons = []
        rid = r.get("_id")
        # required fields
        for fld in ["title", "prep_time_minutes", "cook_time_minutes", "difficulty", "ingredients", "steps"]:
            if fld not in r or r.get(fld) in (None, "", []):
                reasons.append(f"missing_or_empty:{fld}")
        # numeric checks
        if "prep_time_minutes" in r and (not isinstance(r["prep_time_minutes"], (int, float)) or r["prep_time_minutes"] < 0):
            reasons.append("invalid_prep_time")
        if "cook_time_minutes" in r and (not isinstance(r["cook_time_minutes"], (int, float)) or r["cook_time_minutes"] < 0):
            reasons.append("invalid_cook_time")
        # difficulty check
        if r.get("difficulty") not in VALID_DIFFICULTIES:
            reasons.append("invalid_difficulty")
        if reasons:
            invalid.append({"recipe_id": rid, "reasons": reasons})
        else:
            valid.append(rid)
    return valid, invalid

# ---------- Interactions ----------
def validate_interactions():
    items = load(os.path.join(RAW_DIR, "interactions.json"))
    valid = []
    invalid = []
    for it in items:
        reasons = []
        iid = it.get("_id")
        for fld in ["recipe_id", "user_id", "type", "timestamp"]:
            if fld not in it or it.get(fld) in (None, ""):
                reasons.append(f"missing:{fld}")
        if it.get("type") not in VALID_INTERACTION_TYPES:
            reasons.append("invalid_type")
        if reasons:
            invalid.append({"interaction_id": iid, "reasons": reasons})
        else:
            valid.append(iid)
    return valid, invalid

# ---------- Users ----------
def validate_users():
    items = load(os.path.join(RAW_DIR, "users.json"))
    valid = []
    invalid = []
    for u in items:
        reasons = []
        uid = u.get("_id") or u.get("user_id") or u.get("id")
        # required
        if not uid:
            reasons.append("missing:_id")
        # name
        name = u.get("displayName") or u.get("name")
        if not name:
            reasons.append("missing:name")
        # email
        email = u.get("email")
        if not email:
            reasons.append("missing:email")
        else:
            if "@" not in email or "." not in email.split("@")[-1]:
                reasons.append("invalid_email")
        if reasons:
            invalid.append({"user_id": uid, "reasons": reasons})
        else:
            valid.append(uid)
    return valid, invalid

# ---------- Write report ----------
if __name__ == "__main__":
    rec_valid, rec_invalid = validate_recipes()
    it_valid, it_invalid = validate_interactions()
    user_valid, user_invalid = validate_users()

    report = {
        "recipes": {
            "valid_count": len(rec_valid),
            "invalid_count": len(rec_invalid),
            "invalid_rows": rec_invalid
        },
        "interactions": {
            "valid_count": len(it_valid),
            "invalid_count": len(it_invalid),
            "invalid_rows": it_invalid
        },
        "users": {
            "valid_count": len(user_valid),
            "invalid_count": len(user_invalid),
            "invalid_rows": user_invalid
        }
    }

    # JSON report
    out_json = os.path.join(REPORT_DIR, "validation_report.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote detailed JSON report -> {out_json}")

    # CSV summary (tabular)
    out_csv = os.path.join(REPORT_DIR, "validation_summary.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["collection", "valid_count", "invalid_count"])
        writer.writerow(["recipes", len(rec_valid), len(rec_invalid)])
        writer.writerow(["interactions", len(it_valid), len(it_invalid)])
        writer.writerow(["users", len(user_valid), len(user_invalid)])
    print(f"Wrote summary CSV -> {out_csv}")
