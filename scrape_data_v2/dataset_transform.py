"""
transform_tmdb.py
=================
Đọc 2 file CSV gốc từ Kaggle TMDB 5000:
  - tmdb_5000_movies.csv
  - tmdb_5000_credits.csv

Xuất ra 8 file CSV chuẩn hóa:
  cast_info.csv / name.csv / title.csv / movie_keywords.csv
  movie_companies.csv / company_name.csv / keyword.csv / role_type.csv

Cách chạy:
  python transform_tmdb.py
  hoặc chỉ định đường dẫn:
  python transform_tmdb.py --movies /path/to/tmdb_5000_movies.csv \
                           --credits /path/to/tmdb_5000_credits.csv \
                           --output /path/to/output_folder
"""

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def safe_parse(val):
    """Parse a JSON/Python-literal string; return [] on failure."""
    if pd.isna(val):
        return []
    if isinstance(val, (list, dict)):
        return val
    val = str(val).strip()
    if not val or val in ("[]", "{}"):
        return []
    try:
        return json.loads(val)
    except Exception:
        try:
            return ast.literal_eval(val)
        except Exception:
            return []


def md5hex(s):
    return hashlib.md5(str(s).encode("utf-8")).hexdigest()


def soundex(name: str) -> str:
    """Classic Soundex – returns a 4-char code, e.g. 'R163'."""
    _map = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6',
    }
    name = ''.join(c for c in name.upper() if c.isalpha())
    if not name:
        return ""
    first = name[0]
    coded = first
    prev  = _map.get(first, '0')
    for ch in name[1:]:
        digit = _map.get(ch, '0')
        if digit != '0' and digit != prev:
            coded += digit
        prev = digit
    return (coded + "000")[:4]


def safe_int(val):
    """Chuyển val sang int; trả về None nếu không hợp lệ."""
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Main transform
# ──────────────────────────────────────────────────────────────────────────────

def transform(movies_path: Path, credits_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] Reading  {movies_path}  ...")
    movies_raw = pd.read_csv(movies_path, dtype=str, low_memory=False, quoting=1,
                             escapechar="\\", on_bad_lines="skip")

    print(f"[2/3] Reading  {credits_path}  ...")
    credits_raw = pd.read_csv(credits_path, dtype=str, low_memory=False, quoting=1,
                              escapechar="\\", on_bad_lines="skip")

    # Normalise column names (strip whitespace)
    movies_raw.columns  = movies_raw.columns.str.strip()
    credits_raw.columns = credits_raw.columns.str.strip()

    # Detect movie-id column in credits (movie_id or id)
    cred_id_col = "movie_id" if "movie_id" in credits_raw.columns else "id"

    print("[3/3] Transforming …")

    # ── role_type ─────────────────────────────────────────────────────────────
    role_set = {"actor"}
    for val in credits_raw["crew"]:
        for c in safe_parse(val):
            job = str(c.get("job", "")).strip()
            if job:
                role_set.add(job)

    roles_df = pd.DataFrame(
        sorted(role_set),
        columns=["cast_role"]
    ).reset_index()
    roles_df.rename(columns={"index": "role_id"}, inplace=True)
    roles_df["role_id"] = roles_df["role_id"] + 1          # 1-based
    role_map      = dict(zip(roles_df["cast_role"], roles_df["role_id"]))
    actor_role_id = role_map["actor"]

    # ── people (name.csv) ─────────────────────────────────────────────────────
    people = {}   # person_id (int) -> row dict

    def add_person(entry: dict):
        pid = safe_int(entry.get("id"))
        if pid is None:
            return
        if pid in people:
            return
        name   = str(entry.get("name", "")).strip()
        parts  = name.split()
        gender = int(entry.get("gender", 0))
        people[pid] = {
            "person_id":   pid,
            "cast_name":   name,
            "imdb_idx":    f"nm{pid:07d}",
            "imdb_id":     pid,
            "cast_gender": gender,
            "name_cf":     name.upper(),
            "name_nf":     f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else name,
            "surname":     parts[-1] if parts else "",
            "md5":         md5hex(name),
        }

    for val in credits_raw["cast"]:
        for c in safe_parse(val):
            add_person(c)
    for val in credits_raw["crew"]:
        for c in safe_parse(val):
            add_person(c)

    names_df = pd.DataFrame(list(people.values()), columns=[
        "person_id", "cast_name", "imdb_idx", "imdb_id",
        "cast_gender", "name_cf", "name_nf", "surname", "md5"
    ])

    # ── title.csv (movies) ────────────────────────────────────────────────────
    mov_id_col = "id" if "id" in movies_raw.columns else movies_raw.columns[0]

    title_rows = []
    skipped_movies = 0
    for _, row in movies_raw.iterrows():
        mid = safe_int(row[mov_id_col])
        if mid is None:
            skipped_movies += 1
            continue
        title = str(row.get("title", "")).strip()
        release_raw = str(row.get("release_date", "")).strip()
        release = release_raw[:10] if len(release_raw) >= 10 else release_raw or None
        title_rows.append({
            "movie_id":     mid,
            "title":        title,
            "imdb_idx":     f"tt{mid:07d}",
            "movie_kind":   "movie",
            "release":      release,
            "imdb_id":      mid,
            "phonetic":     soundex(title),
            "episode_id":   None,
            "season":       None,
            "episode":      None,
            "series_years": None,
            "md5":          md5hex(title),
        })
    if skipped_movies:
        print(f"  ⚠  Bỏ qua {skipped_movies} dòng movies có movie_id không hợp lệ.")

    titles_df = pd.DataFrame(title_rows, columns=[
        "movie_id", "title", "imdb_idx", "movie_kind", "release", "imdb_id",
        "phonetic", "episode_id", "season", "episode", "series_years", "md5"
    ])

    # ── keyword.csv + movie_keywords.csv ──────────────────────────────────────
    kw_registry = {}
    mk_rows     = []
    mkid        = 1

    for _, row in movies_raw.iterrows():
        mid = safe_int(row[mov_id_col])
        if mid is None:
            continue
        seen = set()
        for kw in safe_parse(row.get("keywords", "[]")):
            kid   = safe_int(kw.get("id"))
            if kid is None:
                continue
            kname = str(kw["name"]).strip()
            if kid not in kw_registry:
                kw_registry[kid] = kname
            if (mid, kid) not in seen:
                mk_rows.append({"mkid": mkid, "movie_id": mid, "keyword_id": kid})
                mkid += 1
                seen.add((mid, kid))

    keywords_df = pd.DataFrame(
        [{"keyword_id": k, "keyword": v, "phonetic": soundex(v)} for k, v in kw_registry.items()],
        columns=["keyword_id", "keyword", "phonetic"]
    )
    movie_keywords_df = pd.DataFrame(mk_rows, columns=["mkid", "movie_id", "keyword_id"])

    # ── company_name.csv + movie_companies.csv ────────────────────────────────
    co_registry = {}
    mc_rows     = []
    mcid        = 1

    for _, row in movies_raw.iterrows():
        mid = safe_int(row[mov_id_col])
        if mid is None:
            continue
        seen = set()
        for co in safe_parse(row.get("production_companies", "[]")):
            cid = safe_int(co.get("id"))
            if cid is None:
                continue
            cname = str(co["name"]).strip()
            if cid not in co_registry:
                co_registry[cid] = cname
            if (mid, cid) not in seen:
                mc_rows.append({
                    "mcid":       mcid,
                    "movie_id":   mid,
                    "company_id": cid,
                    "ctype":      "production",
                    "note":       None,
                })
                mcid += 1
                seen.add((mid, cid))

    companies_df = pd.DataFrame([
        {
            "company_id": cid,
            "name":       name,
            "country":    None,
            "imdb_id":    cid,
            "name_nf":    name.upper(),
            "name_sf":    soundex(name),
            "md5":        md5hex(name),
        }
        for cid, name in co_registry.items()
    ], columns=["company_id", "name", "country", "imdb_id", "name_nf", "name_sf", "md5"])

    movie_companies_df = pd.DataFrame(mc_rows, columns=["mcid", "movie_id", "company_id", "ctype", "note"])

    # ── cast_info.csv ─────────────────────────────────────────────────────────
    cast_rows = []
    cast_id   = 1
    skipped_credits = 0

    valid_movie_ids = set(titles_df["movie_id"])

    for _, row in credits_raw.iterrows():
        mid = safe_int(row[cred_id_col])
        if mid is None:
            skipped_credits += 1
            continue
        if mid not in valid_movie_ids:
            continue

        # Cast members
        for c in safe_parse(row.get("cast", "[]")):
            pid = safe_int(c.get("id"))
            if pid is None:
                continue
            cast_rows.append({
                "cast_id":        cast_id,
                "person_id":      pid,
                "movie_id":       mid,
                "person_role_id": None,
                "note":           str(c.get("character", "")).strip() or None,
                "nr_order":       int(c["order"]) if str(c.get("order", "")).strip().lstrip("-").isdigit() else None,
                "role_id":        actor_role_id,
            })
            cast_id += 1

        # Crew members
        for c in safe_parse(row.get("crew", "[]")):
            pid = safe_int(c.get("id"))
            if pid is None:
                continue
            job = str(c.get("job", "")).strip()
            cast_rows.append({
                "cast_id":        cast_id,
                "person_id":      pid,
                "movie_id":       mid,
                "person_role_id": None,
                "note":           str(c.get("department", "")).strip() or None,
                "nr_order":       None,
                "role_id":        role_map.get(job),
            })
            cast_id += 1

    if skipped_credits:
        print(f"  ⚠  Bỏ qua {skipped_credits} dòng credits có movie_id không hợp lệ.")

    cast_df = pd.DataFrame(cast_rows, columns=[
        "cast_id", "person_id", "movie_id", "person_role_id", "note", "nr_order", "role_id"
    ])

    # ── Write output CSVs ─────────────────────────────────────────────────────
    outputs = {
        "cast_info.csv":       cast_df,
        "name.csv":            names_df,
        "title.csv":           titles_df,
        "movie_keywords.csv":  movie_keywords_df,
        "movie_companies.csv": movie_companies_df,
        "company_name.csv":    companies_df,
        "keyword.csv":         keywords_df,
        "role_type.csv":       roles_df,
    }

    print()
    for fname, df in outputs.items():
        path = output_dir / fname
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  ✓  {fname:<25}  {len(df):>8,} rows   →  {path}")

    print("\n✅  All done.")


# ──────────────────────────────────────────────────────────────────────────────
# Entry-point
# ──────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Transform TMDB-5000 CSVs into normalised tables.")
    p.add_argument(
        "--movies",
        default="tmdb_5000_movies.csv",
        help="Path to tmdb_5000_movies.csv  (default: ./tmdb_5000_movies.csv)",
    )
    p.add_argument(
        "--credits",
        default="tmdb_5000_credits.csv",
        help="Path to tmdb_5000_credits.csv (default: ./tmdb_5000_credits.csv)",
    )
    p.add_argument(
        "--output",
        default="output",
        help="Output folder (default: ./output)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    movies_path  = Path(args.movies)
    credits_path = Path(args.credits)
    output_dir   = Path(args.output)

    missing = [p for p in (movies_path, credits_path) if not p.exists()]
    if missing:
        print("❌  File(s) not found:")
        for m in missing:
            print(f"      {m}")
        print("\nUsage:  python transform_tmdb.py --movies <path> --credits <path> --output <folder>")
        sys.exit(1)

    transform(movies_path, credits_path, output_dir)