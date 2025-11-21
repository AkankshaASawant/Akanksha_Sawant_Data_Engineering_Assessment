# analytics.py
"""
Improved analytics script:
 - Reads CSVs from outputs/csv
 - Produces outputs/reports/analytics_summary.md (Markdown tables)
 - Exports per-insight CSVs to outputs/reports for ease of review
Usage:
    python analytics.py
"""
import os
import pandas as pd
import numpy as np

CSV_DIR = "outputs/csv"
REPORT_DIR = "outputs/reports"
os.makedirs(REPORT_DIR, exist_ok=True)

recipes_path = os.path.join(CSV_DIR, "recipes.csv")
ingredients_path = os.path.join(CSV_DIR, "ingredients.csv")
interactions_path = os.path.join(CSV_DIR, "interactions.csv")
users_path = os.path.join(CSV_DIR, "users.csv")

for p in [recipes_path, ingredients_path, interactions_path, users_path]:
    if not os.path.exists(p):
        raise FileNotFoundError(f"{p} missing. Run transform_to_csv.py first.")

recipes = pd.read_csv(recipes_path)
ingredients = pd.read_csv(ingredients_path)
interactions = pd.read_csv(interactions_path)
users = pd.read_csv(users_path)

# ensure ids are strings
recipes['recipe_id'] = recipes['recipe_id'].astype(str)
ingredients['recipe_id'] = ingredients['recipe_id'].astype(str)
interactions['recipe_id'] = interactions['recipe_id'].astype(str)
interactions['user_id'] = interactions['user_id'].astype(str)
users['user_id'] = users['user_id'].astype(str)

# helper to write df markdown & csv
def write_df_md_csv(df, title, fname):
    md_path = os.path.join(REPORT_DIR, "analytics_summary.md")
    # append markdown table
    with open(md_path, "a", encoding="utf-8") as f:
        f.write(f"## {title}\n\n")
        if df.empty:
            f.write("_No data available_\n\n")
        else:
            f.write(df.to_markdown(index=False))
            f.write("\n\n")
    # also save CSV for this insight
    df.to_csv(os.path.join(REPORT_DIR, fname), index=False)

# create/overwrite markdown header
md_path = os.path.join(REPORT_DIR, "analytics_summary.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# 📊 Analytics Summary\n\n")
    f.write(f"Generated: {pd.Timestamp.now()}\n\n")

# 1. Most common ingredients
most_common_ings = ingredients['name'].value_counts().reset_index()
most_common_ings.columns = ['ingredient', 'count']
most_common_ings = most_common_ings.head(20)
write_df_md_csv(most_common_ings, "Top Ingredients (by frequency)", "top_ingredients.csv")

# 2. Average preparation time
avg_prep = recipes['prep_time_minutes'].dropna().astype(float).mean()
with open(md_path, "a", encoding="utf-8") as f:
    f.write("## Average Preparation Time\n\n")
    f.write(f"**{avg_prep:.2f} minutes**\n\n")

# 3. Difficulty distribution
difficulty_dist = recipes['difficulty'].value_counts().reset_index()
difficulty_dist.columns = ['difficulty', 'count']
write_df_md_csv(difficulty_dist, "Difficulty Distribution", "difficulty_distribution.csv")

# 4. Correlation between prep time and likes
inter_counts = interactions.groupby(['recipe_id', 'type']).size().unstack(fill_value=0)
likes = inter_counts.get('like', pd.Series(dtype=int))
likes = likes.reindex(recipes['recipe_id']).fillna(0).astype(float)
prep = recipes.set_index('recipe_id')['prep_time_minutes'].reindex(likes.index).fillna(0).astype(float)
corr = None
if len(prep) > 1:
    try:
        corr = float(np.corrcoef(prep, likes)[0, 1])
    except Exception:
        corr = None
with open(md_path, "a", encoding="utf-8") as f:
    f.write("## Correlation: Preparation Time vs Likes\n\n")
    f.write(f"**Correlation (pearson):** {corr}\n\n")

# 5. Most frequently viewed recipes (with titles)
views = inter_counts.get('view', pd.Series(dtype=int)).reset_index().rename(columns={0: 'views'})
views = views.merge(recipes[['recipe_id', 'title']], on='recipe_id', how='left').fillna({'title': ''})
views = views[['title', 'recipe_id', 'view']].rename(columns={'view': 'views'}).sort_values('views', ascending=False)
views_top = views.head(20)
write_df_md_csv(views_top, "Top Viewed Recipes", "top_viewed_recipes.csv")

# 6. Ingredients associated with high engagement (recipes in top 25% likes)
likes_series = inter_counts.get('like', pd.Series(dtype=int))
if not likes_series.empty:
    threshold = likes_series.quantile(0.75)
    high_eng_recipe_ids = likes_series[likes_series >= threshold].index.tolist()
    high_ing = ingredients[ingredients['recipe_id'].isin(high_eng_recipe_ids)]['name'].value_counts().reset_index()
    high_ing.columns = ['ingredient', 'count']
else:
    high_ing = pd.DataFrame(columns=['ingredient', 'count'])
write_df_md_csv(high_ing.head(20), "Ingredients in High-Engagement Recipes", "high_engagement_ingredients.csv")

# 7. Average cook time
avg_cook = recipes['cook_time_minutes'].dropna().astype(float).mean()
with open(md_path, "a", encoding="utf-8") as f:
    f.write("## Average Cook Time\n\n")
    f.write(f"**{avg_cook:.2f} minutes**\n\n")

# 8. Average total time (prep + cook)
avg_total = (recipes['prep_time_minutes'].fillna(0).astype(float) + recipes['cook_time_minutes'].fillna(0).astype(float)).mean()
with open(md_path, "a", encoding="utf-8") as f:
    f.write("## Average Total Time (prep + cook)\n\n")
    f.write(f"**{avg_total:.2f} minutes**\n\n")

# 9. Top recipes by attempts
attempts = inter_counts.get('cook_attempt', pd.Series(dtype=int)).reset_index().rename(columns={0: 'attempts'})
attempts = attempts.merge(recipes[['recipe_id', 'title']], on='recipe_id', how='left')
attempts = attempts[['title', 'recipe_id', 'cook_attempt']].rename(columns={'cook_attempt': 'attempts'}).sort_values('attempts', ascending=False)
attempts_top = attempts.head(20)
write_df_md_csv(attempts_top, "Top Recipes by Cook Attempts", "top_attempts.csv")

# 10. Likes per difficulty (average likes per difficulty level)
likes_df = pd.DataFrame({'recipe_id': likes_series.index, 'likes': likes_series.values})
likes_by_diff = recipes.merge(likes_df, on='recipe_id', how='left').fillna({'likes': 0}).groupby('difficulty')['likes'].mean().reset_index()
likes_by_diff.columns = ['difficulty', 'avg_likes']
write_df_md_csv(likes_by_diff, "Average Likes per Difficulty", "likes_per_difficulty.csv")

# ---- USER ANALYTICS (optional but included) ----
# Total users
total_users = len(users)
with open(md_path, "a", encoding="utf-8") as f:
    f.write("## User Analytics\n\n")
    f.write(f"**Total users:** {total_users}\n\n")

# New users per day (if created_at parseable)
try:
    users['created_at'] = pd.to_datetime(users['created_at'])
    users_per_day = users.groupby(users['created_at'].dt.date).size().reset_index()
    users_per_day.columns = ['date', 'new_users']
except Exception:
    users_per_day = pd.DataFrame(columns=['date', 'new_users'])
write_df_md_csv(users_per_day, "New Users Per Day", "users_per_day.csv")

# Most active users (by interaction count)
user_activity = interactions['user_id'].value_counts().reset_index()
user_activity.columns = ['user_id', 'interaction_count']
user_activity = user_activity.merge(users[['user_id','name']], on='user_id', how='left').fillna({'name': ''})
write_df_md_csv(user_activity.head(50), "Most Active Users (by interaction count)", "most_active_users.csv")

# Users with no interactions
inactive_users = users[~users['user_id'].isin(user_activity['user_id'])]
write_df_md_csv(inactive_users[['user_id','name','email','created_at']].reset_index(drop=True), "Users with No Interactions", "inactive_users.csv")

print(f"Saved improved analytics to {md_path} and supporting CSVs in {REPORT_DIR}")
