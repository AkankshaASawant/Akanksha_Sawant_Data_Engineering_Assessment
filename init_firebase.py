"""
Improved Firestore Seeder for:
 - Candidate recipe: Prawns Biryani (akanksha_recipe)
 - 15 realistic synthetic recipes
 - 10 synthetic users with names + timestamps
 - Synthetic interactions (views, likes, cook_attempt)

Run:
    python init_firebase.py
"""

import firebase_admin
from firebase_admin import credentials, firestore
from faker import Faker
import random
import uuid
import datetime
import os

# ----------------------------
# Load Service Account
# ----------------------------
KEY_PATH = "serviceAccountKey.json"
if not os.path.exists(KEY_PATH):
    raise FileNotFoundError(
        f"❌ serviceAccountKey.json not found at {KEY_PATH}. Place it in the project root."
    )

cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()
fake = Faker()

# ----------------------------
# Timestamp Helper
# ----------------------------
def timestamp():
    return datetime.datetime.now(datetime.timezone.utc)

# ----------------------------
# Synthetic Generators
# ----------------------------

REAL_INGREDIENTS = [
    "Onion", "Tomato", "Garlic", "Ginger", "Green Chilli", "Coriander",
    "Cumin Seeds", "Turmeric Powder", "Red Chilli Powder", "Salt",
    "Black Pepper", "Olive Oil", "Vegetable Oil", "Butter", "Milk",
    "Basmati Rice", "Chicken", "Prawns", "Potato", "Carrot",
    "Peas", "Bell Pepper", "Coconut Milk", "Mustard Seeds"
]

UNITS = ["g", "ml", "tbsp", "tsp", "cups", "pieces"]

def generate_ingredients(n=5):
    ingredients = []
    for _ in range(n):
        ingredients.append({
            "name": random.choice(REAL_INGREDIENTS),
            "quantity": f"{random.randint(1, 500)} {random.choice(UNITS)}"
        })
    return ingredients


def generate_recipe_title():
    mains = ["Curry", "Biryani", "Masala", "Stew", "Soup", "Pasta", "Salad", "Fry"]
    items = ["Chicken", "Paneer", "Mushroom", "Vegetable", "Egg", "Fish", "Potato"]
    return f"{random.choice(items)} {random.choice(mains)}"


def generate_recipe_description():
    descriptions = [
        "A flavorful homemade dish made with aromatic spices and fresh ingredients.",
        "A simple and delicious recipe perfect for weekday dinners.",
        "A rich, creamy, and comforting preparation with balanced spices.",
        "A classic traditional dish enjoyed across households.",
        "A quick and healthy comfort meal ideal for busy days."
    ]
    return random.choice(descriptions)


def generate_tags():
    tag_pool = ["indian", "spicy", "dinner", "lunch", "quick", "comfort-food",
                "traditional", "non-veg", "veg", "easy"]
    return random.sample(tag_pool, random.randint(1, 4))


def generate_steps(n=5):
    sample_steps = [
        "Heat oil in a pan over medium flame.",
        "Add chopped onions and sauté until golden brown.",
        "Add tomatoes and cook until they turn soft.",
        "Mix in the spices and cook for 2–3 minutes.",
        "Add the main ingredient and cook thoroughly.",
        "Simmer on low flame for enhanced flavor.",
        "Garnish with fresh coriander and serve hot."
    ]
    steps = []
    for i in range(n):
        steps.append({
            "order": i + 1,
            "instruction": random.choice(sample_steps)
        })
    return steps


def random_difficulty():
    return random.choice(["easy", "medium", "hard"])


# ----------------------------
# Firebase Collections
# ----------------------------
recipes_col = db.collection("recipes")
users_col = db.collection("users")
interactions_col = db.collection("interactions")

# ----------------------------
# Candidate's Actual Recipe
# ----------------------------
prawns_biryani = {
    "title": "Prawns Biryani",
    "description": "A fragrant and flavorful biryani layered with marinated prawns and aromatic spices.",
    "prep_time_minutes": 30,
    "cook_time_minutes": 45,
    "difficulty": "medium",
    "servings": 2,
    "ingredients": [
        {"name": "Basmati Rice", "quantity": "1 cup"},
        {"name": "Oil", "quantity": "1 tsp"},
        {"name": "Bay Leaf", "quantity": "1"},
        {"name": "Green Cardamom", "quantity": "3-4"},
        {"name": "Cloves", "quantity": "2-3"},
        {"name": "Cumin", "quantity": "1/2 tsp"},
        {"name": "Salt", "quantity": "pinch"},
        {"name": "Water", "quantity": "3-4 cups"},
        {"name": "Prawns (clean & deveined)", "quantity": "250-300 g"},
        {"name": "Biryani Masala", "quantity": "1 tbsp"},
        {"name": "Garam Masala", "quantity": "1/2 tsp"},
        {"name": "Turmeric Powder", "quantity": "1 tsp"},
        {"name": "Chilli Powder", "quantity": "1-2 tsp"},
        {"name": "Ginger Garlic Paste", "quantity": "1 tbsp"},
        {"name": "Onion (sliced)", "quantity": "1 large"},
        {"name": "Tomato (chopped)", "quantity": "1 medium"},
        {"name": "Garlic Cloves", "quantity": "1-3 small"},
        {"name": "Ginger", "quantity": "small piece"},
        {"name": "Coriander Leaves", "quantity": "handful"},
        {"name": "Grated Coconut", "quantity": "2-3 tbsp"},
        {"name": "Coriander Leaves (garnish)", "quantity": "5-7 leaves"},
        {"name": "Grated Coconut (garnish)", "quantity": "2-3 tbsp"}
    ],
    "steps": [
        {"order": 1, "instruction": "Marinate prawns with spices and rest for 30 minutes."},
        {"order": 2, "instruction": "Cook rice with whole spices until 60% done, drain and cool."},
        {"order": 3, "instruction": "Fry onions until golden; blend with tomato, coconut, and aromatics."},
        {"order": 4, "instruction": "Cook prawns in the masala until they turn C-shaped."},
        {"order": 5, "instruction": "Layer rice and masala, cook on low flame (dum) for 20–30 minutes."},
        {"order": 6, "instruction": "Garnish and serve hot with raita."}
    ],
    "tags": ["seafood", "indian", "biryani", "special"],
    "created_at": timestamp()
}

recipes_col.document("akanksha_recipe").set(prawns_biryani)
print("✔ Inserted your recipe as document id 'akanksha_recipe'")

# ----------------------------
# Insert Synthetic Recipes
# ----------------------------
for i in range(1, 16):
    rid = f"recipe_{i}"
    rdoc = {
        "title": generate_recipe_title(),
        "description": generate_recipe_description(),
        "prep_time_minutes": random.randint(10, 40),
        "cook_time_minutes": random.randint(15, 60),
        "difficulty": random_difficulty(),
        "servings": random.randint(1, 6),
        "ingredients": generate_ingredients(random.randint(4, 8)),
        "steps": generate_steps(random.randint(3, 7)),
        "tags": generate_tags(),
        "created_at": timestamp()
    }
    recipes_col.document(rid).set(rdoc)

print("✔ Inserted 15 realistic synthetic recipes")

# ----------------------------
# Insert Synthetic Users
# ----------------------------
user_ids = []
for i in range(1, 11):
    uid = f"user_{i}"
    users_col.document(uid).set({
        "displayName": fake.name(),
        "email": f"user{i}@example.com",
        "joined_at": timestamp()
    })
    user_ids.append(uid)

print("✔ Inserted 10 realistic users")

# ----------------------------
# Insert Interactions
# ----------------------------
interaction_types = ["view", "like", "cook_attempt"]

for recipe_doc in recipes_col.stream():
    recipe_id = recipe_doc.id
    for _ in range(random.randint(5, 40)):
        uid = random.choice(user_ids)
        itype = random.choices(
            interaction_types, weights=[0.7, 0.2, 0.1]
        )[0]

        interactions_col.document(str(uuid.uuid4())).set({
            "recipe_id": recipe_id,
            "user_id": uid,
            "type": itype,
            "timestamp": timestamp(),
            "rating": random.choice([None, 1, 2, 3, 4, 5])
        })

print("✔ Inserted interactions for all recipes")
print("🎉 Firestore Seeding Completed Successfully!")
