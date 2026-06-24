import pandas as pd

# =========================
# 1. LOAD DATA
# =========================

movies = pd.read_csv("movies.csv")
votes = pd.read_csv("tmdb_5000_movies.csv")

# =========================
# 2. JOIN
# =========================

merged = pd.merge(
    movies,
    votes,
    on="movie_id",
    how="left"       # giữ tất cả movie
)
merged['release'] = merged['release'].astype('Int64')
# =========================
# 3. EXPORT
# =========================
merged = merged.drop_duplicates()
merged.to_csv("movies_with_votes.csv", index=False)

print("✅ DONE!")

