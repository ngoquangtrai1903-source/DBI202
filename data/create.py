import pandas as pd

# Đọc file (giả sử tên file là movies.csv)
df = pd.read_csv("movies.csv")

# =========================
# 1. Lấy danh sách genre (các cột từ 'action' trở đi)
# =========================

# Các cột không phải genre
non_genre_cols = ['movie_id', 'title', 'release']

# Lấy danh sách genre
genre_cols = [col for col in df.columns if col not in non_genre_cols]

print("Genres:", genre_cols)

# =========================
# 2. Tạo bảng GENRE
# =========================

genre_df = pd.DataFrame({
    'genre_id': range(1, len(genre_cols) + 1),
    'genre_name': genre_cols
})

print(genre_df.head())

# =========================
# 3. Tạo bảng MOVIE_GENRE
# =========================

movie_genre_list = []

for _, row in df.iterrows():
    movie_id = row['movie_id']

    for genre in genre_cols:
        if row[genre] == 1:
            genre_id = genre_df.loc[genre_df['genre_name'] == genre, 'genre_id'].values[0]

            movie_genre_list.append({
                'movie_id': movie_id,
                'genre_id': genre_id
            })

movie_genre_df = pd.DataFrame(movie_genre_list)

print(movie_genre_df.head())

# =========================
# 4. Export ra file
# =========================

genre_df.to_csv("genre.csv", index=False)
movie_genre_df.to_csv("movie_genre.csv", index=False)

print("✅ Created genre.csv and movie_genre.csv successfully!")