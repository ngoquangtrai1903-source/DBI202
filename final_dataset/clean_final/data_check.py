"""
Script kiểm tra chất lượng dữ liệu cho toàn bộ thư mục CSV.
Check:
1. Khoá chính (PK) - trùng lặp, NULL
2. Khoá ngoại (FK) - tham chiếu không tồn tại (orphan)
3. Lỗi font/encoding - ký tự lạ, mojibake
4. Giá trị NULL/rỗng
5. Kiểu dữ liệu bất thường
6. Duplicate rows
"""

import csv
import os
import re
import sys
from collections import Counter, defaultdict

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== HELPER FUNCTIONS ====================

def read_csv(filename):
    """Đọc file CSV, trả về (headers, rows)"""
    filepath = os.path.join(DATA_DIR, filename)
    rows = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            rows.append(row)
    return headers, rows


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    print(f"\n--- {title} ---")


def print_ok(msg):
    print(f"  ✅ {msg}")


def print_warn(msg):
    print(f"  ⚠️  {msg}")


def print_error(msg):
    print(f"  ❌ {msg}")


def print_info(msg):
    print(f"  ℹ️  {msg}")


# ==================== CHECK FUNCTIONS ====================

def check_encoding_issues(filename, headers, rows):
    """Kiểm tra lỗi font/encoding: ký tự lạ, mojibake, non-ASCII bất thường"""
    issues = []
    # Các pattern phổ biến của mojibake (UTF-8 bị đọc sai encoding)
    mojibake_patterns = [
        r'Ã¡', r'Ã©', r'Ã­', r'Ã³', r'Ãº',  # á é í ó ú bị lỗi
        r'Ã¢', r'Ã£', r'Ã¤', r'Ã¥',           # â ã ä å bị lỗi
        r'Ã¨', r'Ã¬', r'Ã²', r'Ã¹',           # è ì ò ù bị lỗi
        r'Ã§', r'Ã±',                           # ç ñ bị lỗi
        r'Ã¶', r'Ã¼', r'Ã¯',                   # ö ü ï bị lỗi
        r'Ã\x80', r'Ã\x81',                     # control chars
        r'â€™', r'â€œ', r'â€\x9d',             # smart quotes bị lỗi
        r'â€"', r'â€"',                          # em/en dash bị lỗi
        r'Â©', r'Â®', r'Â°',                    # ©®° bị lỗi
        r'ï»¿',                                  # BOM bị lỗi
        r'\ufffd',                                # replacement character
    ]
    
    # Kiểm tra ký tự control (ngoại trừ \n, \r, \t)
    control_char_pattern = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
    
    for row_idx, row in enumerate(rows, start=2):  # row 2 vì header là row 1
        for col in headers:
            val = row.get(col, '')
            if not val:
                continue
            
            # Check mojibake
            for pattern in mojibake_patterns:
                if pattern in val:
                    issues.append({
                        'row': row_idx,
                        'col': col,
                        'value': val[:80],
                        'type': 'mojibake',
                        'detail': f'Phát hiện pattern mojibake: {pattern}'
                    })
                    break
            
            # Check control characters
            if control_char_pattern.search(val):
                issues.append({
                    'row': row_idx,
                    'col': col,
                    'value': repr(val[:80]),
                    'type': 'control_char',
                    'detail': 'Chứa ký tự control bất thường'
                })
            
            # Check replacement character U+FFFD
            if '\ufffd' in val:
                issues.append({
                    'row': row_idx,
                    'col': col,
                    'value': repr(val[:80]),
                    'type': 'replacement_char',
                    'detail': 'Chứa ký tự thay thế U+FFFD (dấu hiệu lỗi encoding)'
                })
    
    return issues


def check_non_ascii_samples(filename, headers, rows):
    """Liệt kê các giá trị chứa ký tự non-ASCII (để review thủ công)"""
    samples = []
    seen = set()
    for row_idx, row in enumerate(rows, start=2):
        for col in headers:
            val = row.get(col, '')
            if not val:
                continue
            non_ascii = [c for c in val if ord(c) > 127]
            if non_ascii and val not in seen:
                seen.add(val)
                samples.append({
                    'row': row_idx,
                    'col': col,
                    'value': val[:100],
                    'non_ascii_chars': list(set(non_ascii))[:10]
                })
            if len(samples) >= 20:  # Giới hạn 20 mẫu
                return samples
    return samples


def check_primary_key(filename, pk_columns, rows):
    """Kiểm tra khoá chính: NULL và trùng lặp"""
    issues = {'null': [], 'duplicate': []}
    
    pk_values = Counter()
    for row_idx, row in enumerate(rows, start=2):
        pk_val = tuple(row.get(col, '').strip() for col in pk_columns)
        
        # Check NULL/empty
        for i, col in enumerate(pk_columns):
            if not pk_val[i]:
                issues['null'].append({'row': row_idx, 'col': col})
        
        pk_values[pk_val] += 1
    
    # Check duplicates
    for pk_val, count in pk_values.items():
        if count > 1:
            issues['duplicate'].append({
                'pk_value': dict(zip(pk_columns, pk_val)),
                'count': count
            })
    
    return issues


def check_foreign_key(child_file, child_col, parent_file, parent_col, child_rows, parent_rows):
    """Kiểm tra khoá ngoại: giá trị con không tồn tại trong bảng cha"""
    parent_values = set()
    for row in parent_rows:
        val = row.get(parent_col, '').strip()
        if val:
            parent_values.add(val)
    
    orphans = []
    for row_idx, row in enumerate(child_rows, start=2):
        val = row.get(child_col, '').strip()
        if val and val not in parent_values:
            orphans.append({
                'row': row_idx,
                'child_col': child_col,
                'value': val
            })
    
    return orphans


def check_nulls_and_empty(filename, headers, rows):
    """Đếm NULL/empty cho mỗi cột"""
    stats = {}
    for col in headers:
        null_count = 0
        empty_count = 0
        for row in rows:
            val = row.get(col)
            if val is None:
                null_count += 1
            elif val.strip() == '':
                empty_count += 1
        stats[col] = {'null': null_count, 'empty': empty_count, 'total': len(rows)}
    return stats


def check_data_types(filename, headers, rows, expected_types):
    """Kiểm tra kiểu dữ liệu: int, float, date, string"""
    issues = []
    
    int_pattern = re.compile(r'^-?\d+$')
    float_pattern = re.compile(r'^-?\d+\.?\d*$')
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}')
    
    for col, expected in expected_types.items():
        if col not in headers:
            continue
        bad_count = 0
        bad_samples = []
        for row_idx, row in enumerate(rows, start=2):
            val = row.get(col, '').strip()
            if not val:
                continue
            
            valid = True
            if expected == 'int':
                valid = bool(int_pattern.match(val))
            elif expected == 'float':
                valid = bool(float_pattern.match(val))
            elif expected == 'date':
                valid = bool(date_pattern.match(val))
            
            if not valid:
                bad_count += 1
                if len(bad_samples) < 5:
                    bad_samples.append({'row': row_idx, 'value': val[:50]})
        
        if bad_count > 0:
            issues.append({
                'col': col,
                'expected': expected,
                'bad_count': bad_count,
                'samples': bad_samples
            })
    
    return issues


def check_duplicate_rows(filename, rows):
    """Kiểm tra dòng trùng lặp hoàn toàn"""
    row_tuples = Counter()
    for row in rows:
        key = tuple(sorted(row.items()))
        row_tuples[key] += 1
    
    duplicates = sum(1 for count in row_tuples.values() if count > 1)
    total_dup_rows = sum(count - 1 for count in row_tuples.values() if count > 1)
    return duplicates, total_dup_rows


# ==================== SCHEMA DEFINITION ====================

# Định nghĩa schema: tên file -> (PK columns, expected types)
SCHEMA = {
    'movies.csv': {
        'pk': ['movie_id'],
        'types': {'movie_id': 'int', 'release': 'int', 'vote_average': 'float', 'vote_count': 'int'}
    },
    'casts.csv': {
        'pk': ['cast_id'],
        'types': {'cast_id': 'int', 'cast_gender': 'int'}
    },
    'movie_cast.csv': {
        'pk': ['cast_id', 'movie_id', 'cast_role'],
        'types': {'cast_id': 'int', 'movie_id': 'int'}
    },
    'genre.csv': {
        'pk': ['genre_id'],
        'types': {'genre_id': 'int'}
    },
    'movie_genre.csv': {
        'pk': ['movie_id', 'genre_id'],
        'types': {'movie_id': 'int', 'genre_id': 'int'}
    },
    'company.csv': {
        'pk': ['company_id'],
        'types': {'company_id': 'int'}
    },
    'companies_movie.csv': {
        'pk': ['movie_id', 'company_id'],
        'types': {'movie_id': 'int', 'company_id': 'int'}
    },
    'keyword.csv': {
        'pk': ['keyword_id'],
        'types': {'keyword_id': 'int'}
    },
    'movie_keyword.csv': {
        'pk': ['movie_id', 'keyword_id'],
        'types': {'movie_id': 'int', 'keyword_id': 'int'}
    },
    'users.csv': {
        'pk': ['user_id'],
        'types': {'user_id': 'int', 'user_age': 'int'}
    },
    'ratings.csv': {
        'pk': ['user_id', 'movie_id'],
        'types': {'user_id': 'int', 'movie_id': 'int', 'rating': 'int', 'rating_timestamp': 'date'}
    },
}

# Định nghĩa quan hệ FK: (child_file, child_col, parent_file, parent_col)
FK_RELATIONS = [
    ('movie_cast.csv', 'cast_id', 'casts.csv', 'cast_id'),
    ('movie_cast.csv', 'movie_id', 'movies.csv', 'movie_id'),
    ('movie_genre.csv', 'movie_id', 'movies.csv', 'movie_id'),
    ('movie_genre.csv', 'genre_id', 'genre.csv', 'genre_id'),
    ('companies_movie.csv', 'movie_id', 'movies.csv', 'movie_id'),
    ('companies_movie.csv', 'company_id', 'company.csv', 'company_id'),
    ('movie_keyword.csv', 'movie_id', 'movies.csv', 'movie_id'),
    ('movie_keyword.csv', 'keyword_id', 'keyword.csv', 'keyword_id'),
    ('ratings.csv', 'user_id', 'users.csv', 'user_id'),
    ('ratings.csv', 'movie_id', 'movies.csv', 'movie_id'),
]


# ==================== MAIN ====================

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║          DATA QUALITY CHECK - DBI202 Clean Final Dataset            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    # Load all data
    data = {}
    total_errors = 0
    total_warnings = 0
    
    print_section("1. LOADING DATA")
    for filename in SCHEMA:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print_error(f"File không tồn tại: {filename}")
            total_errors += 1
            continue
        headers, rows = read_csv(filename)
        data[filename] = {'headers': headers, 'rows': rows}
        print_info(f"{filename}: {len(rows):,} dòng, {len(headers)} cột ({', '.join(headers)})")
    
    # ============ 2. CHECK PRIMARY KEYS ============
    print_section("2. KIỂM TRA KHOÁ CHÍNH (PRIMARY KEY)")
    
    for filename, schema in SCHEMA.items():
        if filename not in data:
            continue
        pk_cols = schema['pk']
        rows = data[filename]['rows']
        
        print_subsection(f"{filename} - PK: {pk_cols}")
        
        pk_issues = check_primary_key(filename, pk_cols, rows)
        
        if pk_issues['null']:
            print_error(f"PK chứa NULL/empty: {len(pk_issues['null'])} trường hợp")
            for issue in pk_issues['null'][:5]:
                print(f"         Dòng {issue['row']}, cột '{issue['col']}'")
            if len(pk_issues['null']) > 5:
                print(f"         ... và {len(pk_issues['null']) - 5} trường hợp khác")
            total_errors += 1
        else:
            print_ok("Không có PK NULL/empty")
        
        if pk_issues['duplicate']:
            print_error(f"PK trùng lặp: {len(pk_issues['duplicate'])} giá trị bị trùng")
            for issue in pk_issues['duplicate'][:5]:
                print(f"         {issue['pk_value']} xuất hiện {issue['count']} lần")
            if len(pk_issues['duplicate']) > 5:
                print(f"         ... và {len(pk_issues['duplicate']) - 5} giá trị khác")
            total_errors += 1
        else:
            print_ok("Không có PK trùng lặp")
    
    # ============ 3. CHECK FOREIGN KEYS ============
    print_section("3. KIỂM TRA KHOÁ NGOẠI (FOREIGN KEY)")
    
    for child_file, child_col, parent_file, parent_col in FK_RELATIONS:
        if child_file not in data or parent_file not in data:
            print_warn(f"Bỏ qua: {child_file}.{child_col} -> {parent_file}.{parent_col} (thiếu dữ liệu)")
            total_warnings += 1
            continue
        
        print_subsection(f"{child_file}.{child_col} → {parent_file}.{parent_col}")
        
        orphans = check_foreign_key(
            child_file, child_col,
            parent_file, parent_col,
            data[child_file]['rows'],
            data[parent_file]['rows']
        )
        
        if orphans:
            print_error(f"Có {len(orphans):,} dòng orphan (FK không tồn tại trong bảng cha)")
            # Tóm tắt unique orphan values
            unique_vals = set(o['value'] for o in orphans)
            print(f"         Số giá trị FK không hợp lệ (unique): {len(unique_vals)}")
            sample_vals = list(unique_vals)[:10]
            print(f"         Mẫu: {sample_vals}")
            total_errors += 1
        else:
            print_ok("Tất cả FK đều hợp lệ")
    
    # ============ 4. CHECK ENCODING/FONT ============
    print_section("4. KIỂM TRA LỖI FONT / ENCODING")
    
    for filename in SCHEMA:
        if filename not in data:
            continue
        
        print_subsection(f"{filename}")
        
        # Check encoding issues
        enc_issues = check_encoding_issues(
            filename, data[filename]['headers'], data[filename]['rows']
        )
        
        if enc_issues:
            mojibake = [i for i in enc_issues if i['type'] == 'mojibake']
            control = [i for i in enc_issues if i['type'] == 'control_char']
            replacement = [i for i in enc_issues if i['type'] == 'replacement_char']
            
            if mojibake:
                print_error(f"Phát hiện {len(mojibake)} trường hợp mojibake (lỗi encoding)")
                for issue in mojibake[:3]:
                    print(f"         Dòng {issue['row']}, cột '{issue['col']}': \"{issue['value']}\"")
                total_errors += 1
            
            if control:
                print_error(f"Phát hiện {len(control)} ký tự control bất thường")
                for issue in control[:3]:
                    print(f"         Dòng {issue['row']}, cột '{issue['col']}': {issue['value']}")
                total_errors += 1
            
            if replacement:
                print_error(f"Phát hiện {len(replacement)} ký tự thay thế U+FFFD")
                for issue in replacement[:3]:
                    print(f"         Dòng {issue['row']}, cột '{issue['col']}': {issue['value']}")
                total_errors += 1
        else:
            print_ok("Không phát hiện lỗi encoding")
        
        # Show non-ASCII samples for review
        non_ascii = check_non_ascii_samples(
            filename, data[filename]['headers'], data[filename]['rows']
        )
        if non_ascii:
            print_info(f"Có {len(non_ascii)} giá trị chứa ký tự non-ASCII (review thủ công):")
            for sample in non_ascii[:5]:
                chars_display = ''.join(sample['non_ascii_chars'][:5])
                print(f"         Dòng {sample['row']}, cột '{sample['col']}': \"{sample['value']}\" [{chars_display}]")
            if len(non_ascii) > 5:
                print(f"         ... và {len(non_ascii) - 5} giá trị khác")
    
    # ============ 5. CHECK NULL/EMPTY VALUES ============
    print_section("5. KIỂM TRA GIÁ TRỊ NULL / RỖNG")
    
    for filename in SCHEMA:
        if filename not in data:
            continue
        
        print_subsection(f"{filename}")
        null_stats = check_nulls_and_empty(
            filename, data[filename]['headers'], data[filename]['rows']
        )
        
        has_issue = False
        for col, stats in null_stats.items():
            total_missing = stats['null'] + stats['empty']
            if total_missing > 0:
                pct = total_missing / stats['total'] * 100
                print_warn(f"Cột '{col}': {total_missing:,} giá trị rỗng ({pct:.1f}%)")
                has_issue = True
                total_warnings += 1
        
        if not has_issue:
            print_ok("Không có giá trị NULL/rỗng")
    
    # ============ 6. CHECK DATA TYPES ============
    print_section("6. KIỂM TRA KIỂU DỮ LIỆU")
    
    for filename, schema in SCHEMA.items():
        if filename not in data:
            continue
        
        print_subsection(f"{filename}")
        
        type_issues = check_data_types(
            filename, data[filename]['headers'], data[filename]['rows'],
            schema.get('types', {})
        )
        
        if type_issues:
            for issue in type_issues:
                print_error(f"Cột '{issue['col']}': {issue['bad_count']:,} giá trị không đúng kiểu '{issue['expected']}'")
                for sample in issue['samples'][:3]:
                    print(f"         Dòng {sample['row']}: \"{sample['value']}\"")
                total_errors += 1
        else:
            print_ok("Tất cả kiểu dữ liệu hợp lệ")
    
    # ============ 7. CHECK DUPLICATE ROWS ============
    print_section("7. KIỂM TRA DÒNG TRÙNG LẶP HOÀN TOÀN")
    
    for filename in SCHEMA:
        if filename not in data:
            continue
        
        dup_groups, dup_rows = check_duplicate_rows(filename, data[filename]['rows'])
        
        if dup_groups > 0:
            print_error(f"{filename}: {dup_groups} nhóm trùng lặp, tổng {dup_rows} dòng thừa")
            total_errors += 1
        else:
            print_ok(f"{filename}: Không có dòng trùng lặp")
    
    # ============ 8. CROSS-TABLE ROW COUNT SUMMARY ============
    print_section("8. TÓM TẮT SỐ DÒNG & THỐNG KÊ")
    
    print(f"\n  {'File':<25} {'Số dòng':>10} {'Số cột':>10}")
    print(f"  {'-'*25} {'-'*10} {'-'*10}")
    for filename in SCHEMA:
        if filename not in data:
            continue
        rows = data[filename]['rows']
        headers = data[filename]['headers']
        print(f"  {filename:<25} {len(rows):>10,} {len(headers):>10}")
    
    # ============ SUMMARY ============
    print_section("KẾT QUẢ TỔNG HỢP")
    print(f"\n  Tổng số lỗi (ERROR):   {total_errors}")
    print(f"  Tổng số cảnh báo (WARN): {total_warnings}")
    
    if total_errors == 0 and total_warnings == 0:
        print("\n  🎉 DỮ LIỆU SẠCH! Không phát hiện vấn đề nào.")
    elif total_errors == 0:
        print("\n  ✅ Không có lỗi nghiêm trọng, nhưng có một số cảnh báo cần lưu ý.")
    else:
        print(f"\n  🔴 Phát hiện {total_errors} lỗi cần khắc phục!")
    
    print()
    return total_errors


if __name__ == '__main__':
    errors = main()
    sys.exit(1 if errors > 0 else 0)
