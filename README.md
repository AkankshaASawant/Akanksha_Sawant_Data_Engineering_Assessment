# Recipe Analytics Pipeline (Firebase-based)

## Overview
This project implements a simple ETL and analytics pipeline that uses Firebase Firestore as the source of truth. It inserts seed recipes, exports Firestore data to JSON, normalizes to CSVs, validates data, and computes analytics.

## Structure
(see Project structure in repository)

## Setup
1. Create Firebase project and Firestore (Native mode)
2. Download service account key and save as serviceAccountKey.json
3. Pip install -r requirements.txt

## Run
1. python init_firebase.py
2. python export_firestore.py
3. python transform_to_csv.py
4. python validate.py
5. python analytics.py

## Data Model
- recipes: recipe metadata, ingredients array, steps array, tags
- users: basic user profile
- interactions: recipe_id, user_id, type (view/like/cook_attempt), timestamp, rating (optional)

(Attach ERD screenshot if required.)

## Validation rules
- Required fields: title, prep_time_minutes, cook_time_minutes, difficulty, ingredients, steps
- prep_time & cook_time must be non-negative
- difficulty ∈ {easy, medium, hard}
- interactions must include recipe_id, user_id, type, timestamp

## Insights
See outputs/reports/analytics_summary.md
See visualizations all the charts and insights


## Security rules
Example rules are in `firestore.rules`. Deploy via `firebase deploy --only firestore:rules`.

## Known constraints
- Admin SDK bypasses security rules; scripts act as server/admin operations.
- For production, use paginated reads and batching for large datasets.
- Timestamps exported as ISO strings; convert as needed.
