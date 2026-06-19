"""
fetch_more_tmdb.py
===================
Cào THÊM phim mới từ TMDb API để bổ sung vào dataset hiện có
(tmdb_5000_movies.csv / tmdb_5000_credits.csv trong repo DBI202).

Khác với dataset gốc (~4.803 phim, dữ liệu cũ tới 2017), script này
lấy phim theo các trang "discover" mới nhất, lọc trùng với các
movie_id đã có sẵn, rồi append vào 2 file CSV gốc — giữ đúng cấu
trúc cột để dataset_transform.py chạy lại không cần sửa gì.

Cách dùng:
    1. pip install requests pandas python-dotenv
    2. Tạo file .env cùng thư mục, nội dung:
         TMDB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    3. python fetch_more_tmdb.py --pages 20 --start_year 2017 --end_year 2026

Lưu ý:
    - TMDB_API_KEY lấy tại: https://www.themoviedb.org/settings/api
    - Mỗi trang discover trả về 20 phim → 20 trang ≈ 400 phim mới
    - Script tự động bỏ qua phim đã có movie_id trùng với file cũ
"""

import argparse
import os
import sys
import time
import json
from pathlib import Path

import pandas as pd
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env optional nếu đã export biến môi trường thủ công

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")


# ──────────────────────────────────────────────────────────────────────────────
def check_api_key():
    if not API_KEY:
        print("❌  Chưa có TMDB_API_KEY.")
        print("    Lấy key tại: https://www.themoviedb.org/settings/api")
        print("    Sau đó tạo file .env với nội dung: TMDB_API_KEY=xxxx")
        sys.exit(1)


def tmdb_get(path: str, params: dict = None) -> dict | None:
    """Gọi GET tới TMDb API, tự retry nếu bị rate-limit (429) hoặc lỗi mạng."""
    params = params or {}
    params["api_key"] = API_KEY
    url = f"{BASE_URL}{path}"

    for attempt in range(5):
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 2))
                print(f"  ⏳  Rate-limited, đợi {wait}s...")
                time.sleep(wait)
                continue
            print(f"  ⚠  Lỗi {r.status_code} cho {url}")
            return None
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            wait = 2 ** attempt  # 1, 2, 4, 8, 16 giây
            print(f"  🔄  Lỗi mạng (lần {attempt+1}/5): {e.__class__.__name__}. Thử lại sau {wait}s...")
            time.sleep(wait)
    return None


# ──────────────────────────────────────────────────────────────────────────────
def discover_movie_ids(pages: int, start_year: int, end_year: int) -> list[int]:
    """Lấy danh sách movie_id mới từ endpoint /discover/movie, sắp xếp theo
    ngày phát hành mới nhất, lọc trong khoảng năm cho trước."""
    ids = []
    print(f"[1/3] Lấy danh sách phim mới ({start_year}-{end_year}), {pages} trang ...")
    for page in range(1, pages + 1):
        data = tmdb_get("/discover/movie", {
            "sort_by": "release_date.desc",
            "primary_release_date.gte": f"{start_year}-01-01",
            "primary_release_date.lte": f"{end_year}-12-31",
            "page": page,
            "language": "en-US",
            "include_adult": "false",
        })
        if not data or "results" not in data:
            break
        for m in data["results"]:
            ids.append(m["id"])
        print(f"  trang {page:>3}: +{len(data['results'])} phim  (tổng {len(ids)})")
        time.sleep(0.05)
    return ids


def fetch_movie_detail(movie_id: int) -> dict | None:
    """Lấy đầy đủ metadata phim, format giống cột trong tmdb_5000_movies.csv
    (dùng append_to_response để gộp keywords vào 1 lần gọi)."""
    data = tmdb_get(f"/movie/{movie_id}", {
        "language": "en-US",
        "append_to_response": "keywords",
    })
    if not data:
        return None

    # Map field "keywords.keywords" → field "keywords" giống file gốc
    kw_obj = data.pop("keywords", {})
    data["keywords"] = json.dumps(kw_obj.get("keywords", []))
    data["genres"] = json.dumps(data.get("genres", []))
    data["production_companies"] = json.dumps(data.get("production_companies", []))
    data["production_countries"] = json.dumps(data.get("production_countries", []))
    data["spoken_languages"] = json.dumps(data.get("spoken_languages", []))
    return data


def fetch_movie_credits(movie_id: int) -> dict | None:
    """Lấy cast + crew, format JSON-stringified giống tmdb_5000_credits.csv."""
    data = tmdb_get(f"/movie/{movie_id}/credits")
    if not data:
        return None
    return {
        "movie_id": movie_id,
        "title": None,  # sẽ điền lại từ movie detail nếu cần
        "cast": json.dumps(data.get("cast", [])),
        "crew": json.dumps(data.get("crew", [])),
    }


# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Cào thêm phim mới từ TMDb API")
    parser.add_argument("--pages", type=int, default=10, help="Số trang discover (mỗi trang ~20 phim)")
    parser.add_argument("--start_year", type=int, default=2017, help="Năm bắt đầu (dataset gốc dừng ở ~2017)")
    parser.add_argument("--end_year", type=int, default=2026, help="Năm kết thúc")
    parser.add_argument("--movies_csv", default="tmdb_5000_movies.csv", help="File movies hiện có")
    parser.add_argument("--credits_csv", default="tmdb_5000_credits.csv", help="File credits hiện có")
    parser.add_argument("--out_movies", default="tmdb_5000_movies.csv", help="File movies đầu ra (ghi đè hoặc mới)")
    parser.add_argument("--out_credits", default="tmdb_5000_credits.csv", help="File credits đầu ra")
    args = parser.parse_args()

    check_api_key()

    # ── Đọc dataset hiện có để biết movie_id nào đã có ──────────────────────
    existing_ids = set()
    movies_old = pd.DataFrame()
    credits_old = pd.DataFrame()

    if Path(args.movies_csv).exists():
        movies_old = pd.read_csv(args.movies_csv, dtype=str, low_memory=False)
        id_col = "id" if "id" in movies_old.columns else movies_old.columns[0]
        existing_ids = set(movies_old[id_col].dropna().astype(int))
        print(f"  Đã có {len(existing_ids)} phim trong {args.movies_csv}")

    if Path(args.credits_csv).exists():
        credits_old = pd.read_csv(args.credits_csv, dtype=str, low_memory=False)

    # ── Bước 1: lấy id phim mới ──────────────────────────────────────────────
    candidate_ids = discover_movie_ids(args.pages, args.start_year, args.end_year)
    new_ids = [i for i in dict.fromkeys(candidate_ids) if i not in existing_ids]
    print(f"\n  → {len(new_ids)} phim mới (sau khi loại trùng với dữ liệu cũ)\n")

    if not new_ids:
        print("Không có phim mới nào để thêm. Dừng.")
        return

    # ── Bước 2: lấy chi tiết từng phim + credits ─────────────────────────────
    print(f"[2/3] Lấy chi tiết {len(new_ids)} phim ...")
    new_movies, new_credits = [], []
    for i, mid in enumerate(new_ids, 1):
        detail = fetch_movie_detail(mid)
        credit = fetch_movie_credits(mid)
        if detail:
            new_movies.append(detail)
        if credit:
            if detail:
                credit["title"] = detail.get("title")
            new_credits.append(credit)
        if i % 25 == 0 or i == len(new_ids):
            print(f"  {i}/{len(new_ids)} phim đã xử lý")
        time.sleep(0.25)

    # ── Bước 3: gộp với dữ liệu cũ và lưu ────────────────────────────────────
    print("[3/3] Gộp và lưu file ...")
    movies_new_df = pd.DataFrame(new_movies)
    credits_new_df = pd.DataFrame(new_credits)

    if not movies_old.empty:
        movies_combined = pd.concat([movies_old, movies_new_df], ignore_index=True)
    else:
        movies_combined = movies_new_df

    if not credits_old.empty:
        credits_combined = pd.concat([credits_old, credits_new_df], ignore_index=True)
    else:
        credits_combined = credits_new_df

    movies_combined.to_csv(args.out_movies, index=False, encoding="utf-8-sig")
    credits_combined.to_csv(args.out_credits, index=False, encoding="utf-8-sig")

    print(f"\n✅  Hoàn tất:")
    print(f"  {args.out_movies}:  {len(movies_combined)} phim (thêm {len(new_movies)})")
    print(f"  {args.out_credits}: {len(credits_combined)} dòng (thêm {len(new_credits)})")
    print(f"\nGợi ý: chạy lại dataset_transform.py để tái tạo 8 bảng chuẩn hoá với dữ liệu mới.")


if __name__ == "__main__":
    main()
