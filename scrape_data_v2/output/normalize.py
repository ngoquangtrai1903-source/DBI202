import pandas as pd


df_cast_info = pd.read_csv('cast_info.csv')
df_roles = pd.read_csv('role_type.csv')

df_merge = pd.merge(df_cast_info, df_roles, on="role_id", how='inner')

df_merge = df_merge.drop(columns=['role_id'])

df_merge.to_csv('cast_movie_scrape.csv', index=False)



import pandas as pd

# 1. Đường dẫn tới 2 file CSV của bạn
file1_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\companies.csv"
file2_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\scrape_data_v2\output\company_name.csv"

# 2. Đọc dữ liệu từ file
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)
print(len(df1), len(df2))

# 3. Gộp 2 bảng lại với nhau
df_combined = pd.concat([df1, df2], ignore_index=True)

# 4. Xóa các dòng trùng lặp hoàn toàn
df_cleaned = df_combined.drop_duplicates()
print(len(df_cleaned))
# 5. Xuất kết quả ra file mới tên là 'merged_companies.csv' đặt tại Desktop của bạn
output_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\final_dataset\companies.csv"
df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Đã gộp thành công! File lưu tại: {output_path}")
#------------------------------------------------------------------------------------------------------------------
import pandas as pd

# 1. Đường dẫn tới 2 file CSV của bạn
file1_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\companies_movie.csv"
file2_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\scrape_data_v2\output\movie_companies.csv"

# 2. Đọc dữ liệu từ file
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)
print(len(df1), len(df2))
# 3. Gộp 2 bảng lại với nhau
df_combined = pd.concat([df1, df2], ignore_index=True)

# 4. Xóa các dòng trùng lặp hoàn toàn
df_cleaned = df_combined.drop_duplicates()
print(len(df_cleaned))
# 5. Xuất kết quả ra file mới tên là 'merged_companies.csv' đặt tại Desktop của bạn
output_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\final_dataset\movie_companies.csv"
df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Đã gộp thành công! File lưu tại: {output_path}")
#-----------------------------------------------------------------------------------------------
import pandas as pd

# 1. Đường dẫn tới 2 file CSV của bạn
file1_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\movies.csv"
file2_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\scrape_data_v2\output\title.csv"

# 2. Đọc dữ liệu từ file
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

df2['release'] = pd.to_datetime(df2['release'], errors='coerce').dt.year

# Chuyển năm về kiểu số nguyên Int64 (để tránh bị hiển thị dạng float 2026.0 nếu có ô trống)
df2['release'] = df2['release'].astype('Int64')
print(df2.head())
print(len(df1), len(df2))
# 3. Gộp 2 bảng lại với nhau
df_combined = pd.concat([df1, df2], ignore_index=True)

# 4. Xóa các dòng trùng lặp hoàn toàn
df_cleaned = df_combined.drop_duplicates()
print(len(df_cleaned))
# 5. Xuất kết quả ra file mới tên là 'merged_companies.csv' đặt tại Desktop của bạn
output_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\final_dataset\movies.csv"
df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Đã gộp thành công! File lưu tại: {output_path}")
#----------------------------------------------------------------------------------------------
import pandas as pd

# 1. Đường dẫn tới 2 file CSV của bạn
file1_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\cast.csv"
file2_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\scrape_data_v2\output\name.csv"

# 2. Đọc dữ liệu từ file
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)
print(len(df1), len(df2))
# 3. Gộp 2 bảng lại với nhau
df_combined = pd.concat([df1, df2], ignore_index=True)

# 4. Xóa các dòng trùng lặp hoàn toàn
df_cleaned = df_combined.drop_duplicates()
print(len(df_cleaned))
# 5. Xuất kết quả ra file mới tên là 'merged_companies.csv' đặt tại Desktop của bạn
output_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\final_dataset\cast.csv"
df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Đã gộp thành công! File lưu tại: {output_path}")
#-----------------------------------------------------------------------------------
import pandas as pd

# 1. Đường dẫn tới 2 file CSV của bạn
file1_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\cast_movie.csv"
file2_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\scrape_data_v2\output\cast_movie_scrape.csv"

# 2. Đọc dữ liệu từ file
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)
print(len(df1), len(df2))
# 3. Gộp 2 bảng lại với nhau
df_combined = pd.concat([df1, df2], ignore_index=True)

# 4. Xóa các dòng trùng lặp hoàn toàn
df_cleaned = df_combined.drop_duplicates()
print(len(df_cleaned))
# 5. Xuất kết quả ra file mới tên là 'merged_companies.csv' đặt tại Desktop của bạn
output_path = r"C:\Users\ACER\OneDrive\Desktop\DBI202\final_dataset\cast_movie.csv"
df_cleaned.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"Đã gộp thành công! File lưu tại: {output_path}")
#---------------------------------------------------------------------------------------
# =========================
# 1. LOAD DATA
# =========================

old_keyword = pd.read_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\keyword.csv")
new_keyword = pd.read_csv("keyword.csv")

old_mk = pd.read_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\movie_keyword.csv")
new_mk = pd.read_csv("movie_keywords.csv")

# =========================
# 2. CLEAN TEXT (RẤT QUAN TRỌNG)
# =========================

def clean_text(df, col):
    df[col] = df[col].str.lower().str.strip()
    return df

old_keyword = clean_text(old_keyword, "keyword")
new_keyword = clean_text(new_keyword, "keyword")

# =========================
# 3. BUILD GLOBAL KEYWORD DICTIONARY
# =========================

all_keywords = pd.concat([
    old_keyword[['keyword']],
    new_keyword[['keyword']]
]).drop_duplicates().reset_index(drop=True)

# tạo ID mới
all_keywords['keyword_id'] = all_keywords.index + 1

# reorder
all_keywords = all_keywords[['keyword_id', 'keyword']]

print("✅ Total unique keywords:", len(all_keywords))

# =========================
# 4. CREATE MAPPING TABLE
# =========================

# OLD mapping
old_map = old_keyword.merge(
    all_keywords,
    on='keyword'
)[['keyword_id_x', 'keyword_id_y']]

old_map.columns = ['old_keyword_id', 'new_keyword_id']

# NEW mapping
new_map = new_keyword.merge(
    all_keywords,
    on='keyword'
)[['keyword_id_x', 'keyword_id_y']]

new_map.columns = ['old_keyword_id', 'new_keyword_id']

# =========================
# 5. REMAP OLD MOVIE_KEYWORD
# =========================

old_mk = old_mk.merge(
    old_map,
    left_on='keyword_id',
    right_on='old_keyword_id',
    how='inner'
)

old_mk = old_mk[['movie_id', 'new_keyword_id']]
old_mk.columns = ['movie_id', 'keyword_id']

# =========================
# 6. REMAP NEW MOVIE_KEYWORD
# =========================

new_mk = new_mk.merge(
    new_map,
    left_on='keyword_id',
    right_on='old_keyword_id',
    how='inner'
)

new_mk = new_mk[['movie_id', 'new_keyword_id']]
new_mk.columns = ['movie_id', 'keyword_id']

# =========================
# 7. MERGE FINAL DATA
# =========================

final_mk = pd.concat([old_mk, new_mk]).drop_duplicates().reset_index(drop=True)

# =========================
# 8. EXPORT
# =========================

all_keywords.to_csv("keyword_final.csv", index=False)
final_mk.to_csv("movie_keyword_final.csv", index=False)

print("🎉 DONE!")
print("keyword_final.csv & movie_keyword_final.csv created")

# #-------------------------------------------------------------
# import pandas as pd
#
# # =========================
# # 1. LOAD DATA
# # =========================
#
# old_genre = pd.read_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\genre.csv")
# new_genre = pd.read_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\scrape_data_v2\output\genre.csv")
#
# old_mg = pd.read_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\data\movie_genre.csv")
# new_mg = pd.read_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\scrape_data_v2\output\movie_genre.csv")
#
# # =========================
# # 2. CLEAN TEXT
# # =========================
#
# def clean_text(df, col):
#     df[col] = df[col].str.lower().str.strip()
#     return df
#
# old_genre = clean_text(old_genre, "genre_name")
# new_genre = clean_text(new_genre, "genre_name")
#
# # =========================
# # 3. BUILD GLOBAL GENRE TABLE
# # =========================
#
# all_genre = pd.concat([
#     old_genre[['genre_name']],
#     new_genre[['genre_name']]
# ]).drop_duplicates().reset_index(drop=True)
#
# # tạo ID mới
# all_genre['genre_id'] = all_genre.index + 1
#
# # reorder
# all_genre = all_genre[['genre_id', 'genre_name']]
#
# print("✅ Total genre:", len(all_genre))
#
# # =========================
# # 4. CREATE MAPPING
# # =========================
#
# # OLD mapping
# old_map = old_genre.merge(
#     all_genre,
#     on='genre_name'
# )[['genre_id_x', 'genre_id_y']]
#
# old_map.columns = ['old_genre_id', 'new_genre_id']
#
# # NEW mapping
# new_map = new_genre.merge(
#     all_genre,
#     on='genre_name'
# )[['genre_id_x', 'genre_id_y']]
#
# new_map.columns = ['old_genre_id', 'new_genre_id']
#
# # =========================
# # 5. REMAP OLD MOVIE_GENRE
# # =========================
#
# old_mg = old_mg.merge(
#     old_map,
#     left_on='genre_id',
#     right_on='old_genre_id',
#     how='inner'
# )
#
# old_mg = old_mg[['movie_id', 'new_genre_id']]
# old_mg.columns = ['movie_id', 'genre_id']
#
# # =========================
# # 6. REMAP NEW MOVIE_GENRE
# # =========================
#
# new_mg = new_mg.merge(
#     new_map,
#     left_on='genre_id',
#     right_on='old_genre_id',
#     how='inner'
# )
#
# new_mg = new_mg[['movie_id', 'new_genre_id']]
# new_mg.columns = ['movie_id', 'genre_id']
#
# # =========================
# # 7. MERGE FINAL
# # =========================
#
# final_mg = pd.concat([old_mg, new_mg]).drop_duplicates().reset_index(drop=True)
#
# # =========================
# # 8. EXPORT
# # =========================
#
# all_genre.to_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\final_dataset\genre.csv", index=False)
# final_mg.to_csv(r"C:\Users\ACER\OneDrive\Desktop\DBI202\final_dataset\movie_genre.csv", index=False)
#
# print("🎉 DONE!")
#
# #--------------------------------------------------------------------------------------------------