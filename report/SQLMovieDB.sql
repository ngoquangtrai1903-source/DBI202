-- 1. TẠO MỚI DATABASE MOVIE DATABASE SYSTEM
CREATE DATABASE MovieDB;
GO
USE MovieDB;
GO

-- ==========================================
-- 2. TẠO CÁC BẢNG GỐC (MASTER TABLES)
-- ==========================================

-- Bảng 1: Phim (movies) - Bảng trung tâm
CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    title NVARCHAR(255) NOT NULL,
    release INT,                 -- Năm phát hành (1916–2026)
    vote_average FLOAT,          -- Điểm trung bình TMDB (0.0–10.0)
    vote_count INT               -- Số lượt bình chọn trên TMDB
);

-- Bảng 2: Danh mục thể loại (genre)
CREATE TABLE genre (
    genre_id INT PRIMARY KEY,
    genre_name VARCHAR(100) NOT NULL -- Tên thể loại (action, drama, comedy...)
);

-- Bảng 3: Từ khoá nội dung (keyword)
CREATE TABLE keyword (
    keyword_id INT PRIMARY KEY,
    keyword NVARCHAR(255) NOT NULL
);

-- Bảng 4: Công ty sản xuất (company)
CREATE TABLE company (
    company_id INT PRIMARY KEY,
    company_name NVARCHAR(255) NOT NULL
);

-- Bảng 5: Thành viên đoàn phim (casts)
CREATE TABLE casts (
    cast_id INT PRIMARY KEY,
    cast_name NVARCHAR(255) NOT NULL,
    cast_gender INT NOT NULL     -- Giới tính: 0=Không rõ, 1=Nữ, 2=Nam
);

-- Bảng 6: Người dùng hệ thống (users)
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    user_age INT,
    user_gender VARCHAR(10),     -- Giới tính: M = Nam, F = Nữ
    user_occupation NVARCHAR(100),
    user_zipcode VARCHAR(50)     -- Lưu dạng Chuỗi để giữ số 0 đứng đầu
);


-- ==========================================
-- 3. TẠO CÁC BẢNG LIÊN KẾT (JUNCTION TABLES)
-- ==========================================

-- Bảng 7: Liên kết phim – thể loại (movie_genre)
CREATE TABLE movie_genre (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);

-- Bảng 8: Liên kết phim – đoàn phim (movie_cast)
CREATE TABLE movie_cast (
    cast_id INT,
    movie_id INT,
    cast_role NVARCHAR(255),     -- Vai trò: actor, director, producer...
    PRIMARY KEY (cast_id, movie_id, cast_role), -- Khóa chính tổ hợp 3 cột tránh trùng lặp vai trò
    FOREIGN KEY (cast_id) REFERENCES casts(cast_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- Bảng 9: Liên kết phim – từ khoá (movie_keyword)
CREATE TABLE movie_keyword (
    movie_id INT,
    keyword_id INT,
    PRIMARY KEY (movie_id, keyword_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (keyword_id) REFERENCES keyword(keyword_id)
);

-- Bảng 10: Liên kết phim – công ty sản xuất (companies_movie)
CREATE TABLE companies_movie (
    movie_id INT,
    company_id INT,
    PRIMARY KEY (company_id, movie_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (company_id) REFERENCES company(company_id)
);

-- Bảng 11: Đánh giá phim từ người dùng (ratings)
CREATE TABLE ratings (
    user_id INT,
    movie_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5), -- Giới hạn điểm đánh giá từ 1 đến 5 sao
    rating_timestamp DATETIME,                 -- Thời điểm đánh giá dạng ngày giờ
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);