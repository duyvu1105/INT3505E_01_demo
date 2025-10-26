from flask import Flask, jsonify
import sqlite3
from database import init_db, DB_FILE

# Khởi tạo database khi ứng dụng bắt đầu
init_db()

app = Flask(__name__)
port = 3005

def get_db_conn():
    """Kết nối đến database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Giúp truy cập cột bằng tên
    return conn

# API GÂY RA LỖI N+1 QUERY
@app.route('/authors/inefficient', methods=['GET'])
def get_authors_inefficient():
    """
    Lấy danh sách tác giả và sách của họ (cách làm thiếu hiệu quả).
    Gây ra N+1 query.
    """
    print("\n--- Yêu cầu đến /authors/inefficient (N+1 Problem) ---")
    
    conn = get_db_conn()
    cursor = conn.cursor()

    # --- Query 1: Lấy tất cả tác giả ---
    print("1. Query 1: Lấy tất cả tác giả")
    cursor.execute('SELECT * FROM authors')
    authors = [dict(row) for row in cursor.fetchall()]
    
    print(f"   => Tìm thấy {len(authors)} tác giả. Bắt đầu vòng lặp...")

    # --- N Queries: Lấy sách cho từng tác giả ---
    for i, author in enumerate(authors):
        print(f"   {i+2}. Query {i+2}: Lấy sách cho tác giả ID {author['id']}")
        books_cursor = conn.cursor()
        books_cursor.execute('SELECT * FROM books WHERE author_id = ?', (author['id'],))
        author['books'] = [dict(row) for row in books_cursor.fetchall()]

    conn.close()
    
    print(f"--- Hoàn thành: Tổng cộng {1 + len(authors)} queries đã được thực thi ---")
    return jsonify(authors)

# API GIẢI QUYẾT VẤN ĐỀ N+1 (EAGER LOADING)
@app.route('/authors/efficient', methods=['GET'])
def get_authors_efficient():
    """
    Lấy danh sách tác giả và sách của họ (cách làm hiệu quả).
    Chỉ sử dụng 2 queries.
    """
    print("\n--- Yêu cầu đến /authors/efficient (Optimized) ---")
    
    conn = get_db_conn()
    cursor = conn.cursor()

    # --- Query 1: Lấy tất cả tác giả ---
    print("1. Query 1: Lấy tất cả tác giả")
    cursor.execute('SELECT * FROM authors')
    authors = [dict(row) for row in cursor.fetchall()]
    author_map = {author['id']: author for author in authors}
    
    # Khởi tạo list sách rỗng cho mỗi tác giả
    for author in authors:
        author['books'] = []

    author_ids = list(author_map.keys())
    
    if not author_ids:
        conn.close()
        return jsonify(authors)

    # --- Query 2: Lấy tất cả sách của các tác giả đó trong 1 lần ---
    print(f"2. Query 2: Lấy tất cả sách có author_id trong {author_ids}")
    
    placeholders = ', '.join('?' for _ in author_ids)
    query = f'SELECT * FROM books WHERE author_id IN ({placeholders})'
    
    cursor.execute(query, author_ids)
    books = [dict(row) for row in cursor.fetchall()]

    # --- Ghép sách vào tác giả (trong Python, không cần query nữa) ---
    print("   => Ghép sách vào tác giả trong bộ nhớ...")
    for book in books:
        author_id = book['author_id']
        if author_id in author_map:
            author_map[author_id]['books'].append(book)

    conn.close()
    
    print("--- Hoàn thành: Tổng cộng 2 queries đã được thực thi ---")
    return jsonify(list(author_map.values()))

if __name__ == '__main__':
    print(f"N+1 Query Demo API")
    print(f" Running at: http://localhost:{port}")
    print("\nEndpoints:")
    print(f"  GET /authors/inefficient  - Gây ra lỗi N+1")
    print(f"  GET /authors/efficient    - Đã tối ưu")
    app.run(port=port, debug=True)
