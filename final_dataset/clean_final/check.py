import pandas as pd

# -------------------------------------------------------------------------
# ĐIỀU CHỈNH TÊN CỘT THEO FILE THỰC TẾ CỦA BẠN (SỬA Ở ĐÂY NẾU KHÁC)
# -------------------------------------------------------------------------
COL_MOVIE_ID = 'movie_id'
COL_CAST_ID = 'cast_id'
COL_USER_ID = 'user_id'
COL_COMP_ID = 'company_id'
COL_GENRE_ID = 'genre_id'  # Sơ đồ ERD của bạn viết là gende_id
COL_KEY_ID = 'keyword_id'

# Tên khóa chính trong các bảng thực thể gốc (nếu khác bảng liên kết)
MAIN_GENRE_ID = 'genre_id'  # Sơ đồ ERD ghi bảng gốc là gender_id

# -------------------------------------------------------------------------
# 1. ĐỌC TẤT CẢ CÁC FILE DỮ LIỆU
# -------------------------------------------------------------------------
print("=== BƯỚC 1: ĐỌC DỮ LIỆU ===")
try:
    # Các bảng thực thể (Bảng cha)
    df_movies = pd.read_csv('movies.csv')
    df_casts = pd.read_csv('casts.csv')
    df_users = pd.read_csv('users.csv')
    df_company = pd.read_csv('company.csv')
    df_genre = pd.read_csv('genre.csv')
    df_keyword = pd.read_csv('keyword.csv')

    # Các bảng liên kết trung gian (Bảng con)
    df_m_cast = pd.read_csv('movie_cast.csv')
    df_m_genre = pd.read_csv('movie_genre.csv')
    # Nếu file của bạn là companies_movie.csv như trong ảnh:
    df_m_company = pd.read_csv('companies_movie.csv')
    df_m_keyword = pd.read_csv('movie_keyword.csv')
    df_m_rating = pd.read_csv('ratings.csv')  # File thực tế là ratings.csv có chữ 's'

    print("Đọc thành công toàn bộ 11 file dữ liệu!")
except Exception as e:
    print(f"Lỗi đọc file: {e}")
    exit()

# -------------------------------------------------------------------------
# 2. KIỂM TRA MAPPING XUÔI (TỪ BẢNG LIÊN KẾT TRỎ VỀ BẢNG GỐC - LỖI MỒ CÔI)
# -------------------------------------------------------------------------
print("\n=== BƯỚC 2: KIỂM TRA MAPPING XUÔI (FOREIGN KEY CHECK) ===")
has_error_xuoi = False

# Định nghĩa các cặp kiểm tra khóa ngoại (Tên bảng liên kết, DataFrame liên kết, Cột ID, DataFrame gốc, Cột ID gốc)
foreign_key_checks = [
    ('movie_cast', df_m_cast, COL_MOVIE_ID, df_movies, COL_MOVIE_ID),
    ('movie_cast', df_m_cast, COL_CAST_ID, df_casts, COL_CAST_ID),

    ('movie_genre', df_m_genre, COL_MOVIE_ID, df_movies, COL_MOVIE_ID),
    ('movie_genre', df_m_genre, COL_GENRE_ID, df_genre, MAIN_GENRE_ID),

    ('companies_movie', df_m_company, COL_MOVIE_ID, df_movies, COL_MOVIE_ID),
    ('companies_movie', df_m_company, COL_COMP_ID, df_company, COL_COMP_ID),

    ('movie_keyword', df_m_keyword, COL_MOVIE_ID, df_movies, COL_MOVIE_ID),
    ('movie_keyword', df_m_keyword, COL_KEY_ID, df_keyword, COL_KEY_ID),

    ('ratings', df_m_rating, COL_MOVIE_ID, df_movies, COL_MOVIE_ID),
    ('ratings', df_m_rating, COL_USER_ID, df_users, COL_USER_ID)
]

for table_name, df_l, col_l, df_m, col_m in foreign_key_checks:
    mo_coi = df_l[~df_l[col_l].isin(df_m[col_m])]
    count = len(mo_coi)
    if count > 0:
        print(f"❌ LỖI: Bảng '{table_name}' chứa {count} dòng có '{col_l}' mồ côi (không tồn tại trong bảng gốc)!")
        has_error_xuoi = True
    else:
        print(f"✅ Chuẩn: Khóa ngoại '{col_l}' trong bảng '{table_name}' khớp 100% với bảng gốc.")

if not has_error_xuoi:
    print("👉 KẾT LUẬN: Mọi ràng buộc khóa ngoại (Foreign Key) đều HỢP LỆ. SQL sẽ không bị lỗi khi nạp bảng con!")

# -------------------------------------------------------------------------
# 3. KIỂM TRA MAPPING NGƯỢC (TỪ BẢNG GỐC TRỎ SANG BẢNG LIÊN KẾT - LỖI CÔ LẬP)
# -------------------------------------------------------------------------
print("\n=== BƯỚC 3: KIỂM TRA MAPPING NGƯỢC (DỮ LIỆU CÔ LẬP) ===")
has_error_nguoc = False

# 3.1 Kiểm tra phim cô lập (Phim phải xuất hiện trong TẤT CẢ các bảng tương tác)
print("--- Kiểm tra bảng Phim (Movies) ---")
link_tables_for_movies = [
    ('movie_cast', df_m_cast),
    ('movie_genre', df_m_genre),
    ('companies_movie', df_m_company),
    ('movie_keyword', df_m_keyword),
    ('ratings', df_m_rating)
]

for table_name, df_l in link_tables_for_movies:
    co_lap = df_movies[~df_movies[COL_MOVIE_ID].isin(df_l[COL_MOVIE_ID])]
    if len(co_lap) > 0:
        print(f"⚠️ Cảnh báo: Có {len(co_lap)} phim trong 'movies.csv' KHÔNG xuất hiện trong bảng '{table_name}'.")
        has_error_nguoc = True
    else:
        print(f"✅ Chuẩn: Toàn bộ phim đều có liên kết trong bảng '{table_name}'.")

# 3.2 Kiểm tra các thực thể khác bị cô lập
print("\n--- Kiểm tra các bảng danh mục còn lại ---")
other_checks = [
    ('casts.csv', df_casts, COL_CAST_ID, df_m_cast, COL_CAST_ID),
    ('genre.csv', df_genre, MAIN_GENRE_ID, df_m_genre, COL_GENRE_ID),
    ('company.csv', df_company, COL_COMP_ID, df_m_company, COL_COMP_ID),
    ('keyword.csv', df_keyword, COL_KEY_ID, df_m_keyword, COL_KEY_ID),
    ('users.csv', df_users, COL_USER_ID, df_m_rating, COL_USER_ID)
]

for file_name, df_m, col_m, df_l, col_l in other_checks:
    co_lap = df_m[~df_m[col_m].isin(df_l[col_l])]
    if len(co_lap) > 0:
        print(
            f"⚠️ Cảnh báo: Có {len(co_lap)} bản ghi trong '{file_name}' bị cô lập (không có bất kỳ phim nào liên kết).")
        has_error_nguoc = True
    else:
        print(f"✅ Chuẩn: Toàn bộ bản ghi trong '{file_name}' đều có liên kết thực tế.")

if not has_error_nguoc:
    print(
        "\n👉 KẾT LUẬN: Dữ liệu hoàn toàn tinh khiết! Không có phần tử cô lập nào. Ma trận hệ thống khuyến nghị sẽ rất sạch.")
else:
    print(
        "\n💡 LỜI KHUYÊN: Nếu bạn muốn xóa triệt để các phần tử cô lập/mồ côi được cảnh báo ở trên, hãy chạy script làm sạch tương ứng.")
