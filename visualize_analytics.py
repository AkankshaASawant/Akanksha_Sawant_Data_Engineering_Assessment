import pandas as pd
import matplotlib.pyplot as plt
import os

# ===============================
# Load CSVs
# ===============================
CSV_DIR = "outputs/csv"
OUT_DIR = "visualizations"
os.makedirs(OUT_DIR, exist_ok=True)

recipes = pd.read_csv(f"{CSV_DIR}/recipes.csv")
ingredients = pd.read_csv(f"{CSV_DIR}/ingredients.csv")
interactions = pd.read_csv(f"{CSV_DIR}/interactions.csv")
users = pd.read_csv(f"{CSV_DIR}/users.csv") if os.path.exists(f"{CSV_DIR}/users.csv") else None


# =====================================================
# Helper function to save chart
# =====================================================
def save_plot(name):
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/{name}.png")
    plt.clf()


# =====================================================
# 1️⃣ Most Common Ingredients (Bar Chart)
# =====================================================
ing_counts = ingredients["name"].value_counts().head(10)

plt.figure(figsize=(8, 5))
ing_counts.plot(kind="bar", color="steelblue")
plt.title("Top 10 Most Common Ingredients")
plt.xlabel("Ingredient")
plt.ylabel("Frequency")
save_plot("most_common_ingredients")


# =====================================================
# 2️⃣ Prep Time Distribution + Average Prep Time
# =====================================================
plt.figure(figsize=(8, 5))
recipes["prep_time_minutes"].plot(kind="hist", bins=15, color="skyblue", edgecolor="black")
plt.title("Distribution of Preparation Time (Minutes)")
plt.xlabel("Prep Time")
save_plot("average_prep_time_distribution")

plt.figure(figsize=(6, 5))
avg_prep = recipes["prep_time_minutes"].mean()
plt.bar(["Average Prep Time"], [avg_prep], color="blue")
plt.title("Average Preparation Time")
plt.ylabel("Minutes")
save_plot("average_prep_time")


# =====================================================
# 3️⃣ Difficulty Distribution (Pie Chart)
# =====================================================
plt.figure(figsize=(6, 6))
recipes["difficulty"].value_counts().plot(kind="pie", autopct="%1.1f%%")
plt.title("Difficulty Distribution")
save_plot("difficulty_distribution")


# =====================================================
# 4️⃣ Correlation Prep Time vs Likes (Scatter Plot)
# =====================================================
likes = interactions[interactions["type"] == "like"]

# FIX: Name the Series before merging
likes_per_recipe = likes.groupby("recipe_id").size().rename("likes")

merged = recipes.merge(likes_per_recipe, on="recipe_id", how="left").fillna(0)

plt.figure(figsize=(8, 6))
plt.scatter(merged["prep_time_minutes"], merged["likes"], color="purple")
plt.xlabel("Preparation Time (Minutes)")
plt.ylabel("Likes Count")
plt.title("Correlation: Prep Time vs Likes")
save_plot("correlation_prep_time_likes")


# =====================================================
# 5️⃣ Most Frequently Viewed Recipes (Bar Chart)
# =====================================================
views = interactions[interactions["type"] == "view"]
view_counts = views.groupby("recipe_id").size().rename("views").sort_values(ascending=False).head(10)

plt.figure(figsize=(8, 5))
view_counts.plot(kind="bar", color="green")
plt.title("Top 10 Viewed Recipes")
plt.xlabel("Recipe")
plt.ylabel("View Count")
save_plot("top_viewed_recipes")


# =====================================================
# 6️⃣ Ingredients Associated with High Engagement
# =====================================================
like_counts = likes.groupby("recipe_id").size()
threshold = like_counts.quantile(0.75)
high_recipes = like_counts[like_counts >= threshold].index.tolist()

high_ing = ingredients[ingredients["recipe_id"].isin(high_recipes)]
high_ing_counts = high_ing["name"].value_counts().head(10)

plt.figure(figsize=(8, 5))
high_ing_counts.plot(kind="bar", color="orange")
plt.title("Ingredients in High Engagement Recipes")
plt.xlabel("Ingredients")
plt.ylabel("Count")
save_plot("high_engagement_ingredients")


# =====================================================
# 7️⃣ Validation Summary
# =====================================================
validation_path = "outputs/reports/validation_report.json"

if os.path.exists(validation_path):
    import json
    with open(validation_path, "r") as f:
        report = json.load(f)

    valid_recipes = report["recipes"]["valid_count"]
    invalid_recipes = report["recipes"]["invalid_count"]

    plt.figure(figsize=(6, 5))
    plt.bar(["Valid", "Invalid"], [valid_recipes, invalid_recipes], color=["green", "red"])
    plt.title("Recipe Validation Summary")
    save_plot("validation_summary")


# =====================================================
# 8️⃣ Inactive Users
# =====================================================
if users is not None:
    interactions_per_user = interactions.groupby("user_id").size()
    inactive_users = users[~users["user_id"].isin(interactions_per_user.index)]

    plt.figure(figsize=(6, 5))
    plt.bar(["Active Users", "Inactive Users"],
            [len(interactions_per_user), len(inactive_users)],
            color=["blue", "gray"])
    plt.title("Active vs Inactive Users")
    save_plot("inactive_users")


# =====================================================
# 9️⃣ Most Active Users
# =====================================================
active_users = interactions.groupby("user_id").size().sort_values(ascending=False).head(10)

plt.figure(figsize=(8, 5))
active_users.plot(kind="bar", color="brown")
plt.title("Top 10 Most Active Users")
plt.xlabel("User ID")
plt.ylabel("Interactions")
save_plot("most_active_users")


# =====================================================
# 🔟 Likes per Difficulty Level
# =====================================================
likes_df = recipes.merge(likes_per_recipe, on="recipe_id", how="left")
likes_df["likes"] = likes_df["likes"].fillna(0)

likes_by_diff = likes_df.groupby("difficulty")["likes"].mean()

plt.figure(figsize=(8, 5))
likes_by_diff.plot(kind="bar", color="teal")
plt.title("Average Likes per Difficulty")
plt.xlabel("Difficulty")
plt.ylabel("Average Likes")
save_plot("likes_per_difficulty")


# =====================================================
# 1️⃣1️⃣ Users Per Day (Line Chart)
# =====================================================
interactions["date"] = pd.to_datetime(interactions["timestamp"]).dt.date
users_per_day = interactions.groupby("date")["user_id"].nunique()

plt.figure(figsize=(10, 5))
users_per_day.plot(kind="line", marker="o")
plt.title("Users Per Day")
plt.xlabel("Date")
plt.ylabel("Unique Users")
save_plot("users_per_day")


# =====================================================
# 1️⃣2️⃣ Top Viewed Recipes Leaderboard
# =====================================================
plt.figure(figsize=(8, 5))
view_counts.plot(kind="bar", color="darkblue")
plt.title("Top Viewed Recipes (Leaderboard)")
plt.xlabel("Recipe ID")
plt.ylabel("Views")
save_plot("leaderboard_top_viewed")


print("All visualizations saved in visualizations/")
