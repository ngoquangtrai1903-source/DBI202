import pandas as pd

# =========================
# 1. Đọc dữ liệu
# =========================

rating_df = pd.read_csv("ratings.csv")
movies_df = pd.read_csv("movies.csv")

# =========================
# 2. Join để map ID
# =========================

merged_df = pd.merge(
    rating_df,
    movies_df[['movie_id_ml', 'movie_id']],  # chỉ lấy cột cần
    on='movie_id_ml',
    how='inner'  # chỉ giữ record match
)

# =========================
# 3. Drop cột cũ (movie_id_ml)
# =========================

normalized_df = merged_df.drop(columns=['movie_id_ml'])

# =========================
# 4. Sắp xếp lại cột (optional)
# =========================

normalized_df = normalized_df[[
    'user_id',
    'movie_id',   # ID chuẩn
    'rating',
    'rating_timestamp'
]]

# =========================
# 5. Export
# =========================

normalized_df.to_csv("rating_normalized.csv", index=False)

print("✅ Created rating_normalized.csv successfully!")