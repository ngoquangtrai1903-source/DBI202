import pandas as pd

# =========================
# 1. LOAD DATA
# =========================

movies = pd.read_csv("movies.csv")
movie_genre = pd.read_csv("movie_genre.csv")

# =========================
# 2. GIỮ LẠI movie CÓ genre
# =========================

movies_clean = movies[movies["movie_id"].isin(movie_genre["movie_id"])]
movies_clean['release'] = movies_clean['release'].astype('Int64')
# =========================
# 3. RESET INDEX
# =========================

movies_clean = movies_clean.reset_index(drop=True)

# =========================
# 4. EXPORT
# =========================

movies_clean.to_csv("movies_clean.csv", index=False)

print("✅ DONE!")
print("Số movie ban đầu:", len(movies))
print("Số movie sau khi clean:", len(movies_clean))