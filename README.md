# 🍽️ Firestore → ETL → Recipe Analytics Pipeline 

A fully automated pipeline for extracting Firestore data, validating it, transforming it into structured CSVs, and generating analytics (both tabular and visual).
Now includes: clean schema documentation, Firebase initialization explanation, and environment requirements.

---
## Structure
<img width="621" height="1022" alt="recipr-pipeline drawio" src="https://github.com/user-attachments/assets/bed20e96-f569-4a7d-8499-6ecdf4a999f9" />

---
# 📦 Requirements

Before running the pipeline, ensure the following are installed and configured:

### **1. Python Environment**

* Python **3.8+**
* Recommended: create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate       # Windows
```

### **2. Install Required Libraries**

```bash
pip install -r requirements.txt
```

Typical dependencies:

* `firebase-admin`
* `pandas`
* `numpy`
* `matplotlib`
* `seaborn`
* `python-dotenv`

### **3. Firebase Service Account Key**

Place a file named **serviceAccountKey.json** in the project directory.
This is required for Firebase Admin SDK authentication.

---

# ⚙️ init_firebase.py

This script configures Firebase Admin SDK and initializes the Firestore client.

### **Purpose of `init_firebase.py`:**

* Loads **serviceAccountKey.json**
* Initializes Firebase Admin App only **once**
* Exports a reusable Firestore client

## **Notes for Data Generation Functions**

### `timestamp()`

```python
# NOTE: Returns the current UTC timestamp for consistent Firestore date fields.
```

### `generate_ingredients(n=5)`

```python
# NOTE: Generates a list of n random ingredients with realistic names and quantities.
```

### `generate_recipe_title()`

```python
# NOTE: Creates a natural-sounding recipe title using random dish + ingredient.
```

### `generate_recipe_description()`

```python
# NOTE: Returns a short, human-like recipe description from a preset list.
```

### `generate_tags()`

```python
# NOTE: Randomly selects 1–4 tags to categorize the recipe.
```

### `generate_steps(n=5)`

```python
# NOTE: Generates ordered cooking steps using realistic cooking instructions.
```

### `random_difficulty()`

```python
# NOTE: Randomly returns a difficulty label: easy / medium / hard.
```

### Firestore collection variables

```python
# NOTE: These variables reference Firestore collections used for seeding.
```

---

Example:

```python
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()
```

All other scripts can simply import:

```python
from init_firebase import db
```

---

# 📌 1. Data Model Overview

The pipeline works with **four primary collections** exported from Firestore (plus Steps).

---

## **1. Recipes**

| Field             | Type     | Description                             |
| ----------------- | -------- | --------------------------------------- |
| recipe_id         | varchar  | Unique ID                            PK |
| title             | string   | Recipe title                            |
| description       | string   | Short description of the recipe         |
| prep_time_minutes | integer  | Preparation time (min)                  |
| cook_time_minutes | integer  | Cooking time (min)                      |
| difficulty        | string   | One of: *easy / medium / hard*          |
| servings          | integer  | Number of servings                      |
| tags              | array    | List of categories/tags                 |
| created_at        | datetime | Timestamp of creation (ISO datetime) FK |

---

## **2. Ingredients**

Flattened after transformation.

| Field            | Type    | Description                            |
| ---------------- | ------- | -------------------------------------- |
| recipe_id        | varchar | Unique ID                           FK |
| ingredient_order | integer | Position in the list                   |
| name             | string  | Name of ingredient                     |
| quantity         | varchar | Measurement/amount                     |

---

## **3. Interactions**

Tracks user behavior.

| Field          | Type      | Description                        |
| -------------- | --------- | ---------------------------------- |
| interaction_id | string    | Unique ID                       PK |
| recipe_id      | string    | Recipe the user interacted with FK |
| user_id        | string    | User performing the interaction FK |
| type           | string    | view / like / cook_attempt         |
| timestamp      | timestamp | When it occurred                   |
| rating         | integer   | Optional user rating               |

---

## **4. Users**

| Field      | Type      | Description                             |
| ---------- | --------- | --------------------------------------- |
| user_id    | varchar   | Unique ID                            PK |
| name       | string    | User's name                             |
| email      | varchar   | User's email                            |
| created_at | timestamp | Timestamp of signup                     |

---

## **5. Steps**

| Field       | Type    | Description                          |
| ----------- | ------- | ------------------------------------ |
| recipe_id   | varchar | Recipe this belongs to            FK |
| step_order  | integer | Order number of the step             |
| instruction | string  | Cooking instruction                  |

---

<img width="940" height="766" alt="image" src="https://github.com/user-attachments/assets/3e63bf24-08b0-4c10-a018-52c1d035a885" />

## Relationships summary
•	Users -> Interactions: 1-to-many (one user may perform many interactions)

•	Recipes -> Ingredients: 1-to-many (each recipe has multiple ingredients)

•	Recipes -> Steps: 1-to-many (ordered steps per recipe)

•	Recipes -> Interactions: 1-to-many (many users interact with a recipe)

•	Users -> Recipes: optional 1-to-many (one user can upload many recipes at created_by)

---

# 📌 2. How to Run the Pipeline (Step-by-Step)

## **STEP 1 — Export Firestore Data**

```bash
python export_firestore.py
```

## **Notes for Firestore Export Script (`export_firestore.py`)**

### `init_firestore_client()`

```python
# NOTE: Initializes the Firestore client, using emulator if available or service account in production.
```

### `doc_to_jsonable(d)`

```python
# NOTE: Converts a Firestore document into a JSON-serializable dictionary with ISO timestamp formatting.
```

### `export_collection(name)`

```python
# NOTE: Streams all documents from a Firestore collection and writes them to a local JSON file.
```

→ outputs `raw_json/`

---

## **STEP 2 — Transform JSON → CSV**

```bash
python transform_to_csv.py
```

## **Notes for CSV Transformation Script (`transform_to_csv.py`)**

### `load_json(fname)`

```python
# NOTE: Loads a JSON file from the raw exports directory and returns the parsed list/dict.
```

### `transform_recipes()`

```python
# NOTE: Normalizes recipe, ingredient, and step data into separate CSV tables.
```

### `transform_interactions()`

```python
# NOTE: Converts interaction JSON documents into a flat interactions.csv table.
```

### `transform_users()`

```python
# NOTE: Normalizes user records into a consistent users.csv file, handling multiple field naming styles.
```

→ outputs `csv/`

---

## **STEP 3 — Validate Data**

```bash
python validate.py
```

## **Notes for Validation Script (`validate.py`)**

### `load(path)`

```python
# NOTE: Loads a JSON file from disk and returns its parsed content.
```

### `validate_recipes()`

```python
# NOTE: Validates recipe documents for required fields, numeric checks, and allowed difficulty values.
```

### `validate_interactions()`

```python
# NOTE: Validates interaction records ensuring required fields and valid interaction type.
```

### `validate_users()`

```python
# NOTE: Validates user documents by checking ID, name, and email format correctness.
```

→ outputs `validation_report.json`, `validation_summary.csv`

---

## **STEP 4 — Generate Analytics (Tabular)**

```bash
python analytics.py
```

## **Notes for Analytics Script (`analytics.py`)**

### `write_df_md_csv(df, title, fname)`

```python
# NOTE: Writes a DataFrame into the main analytics_summary.md file and also exports a CSV for detailed review.
```

Additional section notes:

```python
# NOTE: Loads all CSVs and normalizes ID columns for consistent merging.
# NOTE: Computes ingredient frequency, difficulty counts, prep-time averages, etc.
# NOTE: Identifies high-engagement ingredients and trending recipes.
# NOTE: Performs basic user analytics: active users, inactive users, signups.
```

→ outputs `analytics_summary`

---


## **STEP 5 — Generate Visual Analytics**

```bash
python visual_analytics.py
```
## **F. Notes for Visual Analytics Script (`visual_analytics.py`)**

### `save_plot(name)`

```python
# NOTE: Saves the current Matplotlib figure as a PNG file and clears the plot for the next chart.
```

→ outputs `visualizations/`

---

# 📌 3. ETL Process Overview

**Extraction → Transformation → Loading**

* Exports JSON from Firestore
* Flattens nested arrays + timestamps
* Saves clean CSVs
* Ready for BI tools or ML models

---

# 📌 4. Insights Summary

* Top ingredients
* Difficulty distribution
* Trending recipes
* User activity
* Engagement patterns
* Validation errors

---

# 📌 5. Known Constraints & Limitations

* Assumes standard Firestore structure
* Timestamps inconsistent depending on Firestore source
* Validation rules minimal
* Ingredient text may require better normalization

---

# 📌 Final Summary

This project provides a complete **end-to-end ETL + analytics** solution for recipe datasets sourced from Firestore.
You now have:

* Clean Firestore extraction
* Structured transformations
* Automated validation
* Tabular + visual analytics
* Reusable CSV outputs
* Fully documented pipeline
* Function-specific notes for all scripts

---
