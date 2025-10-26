import sqlite3
import os

DB_FILE = 'n_plus_1_demo.db'

def init_db():
    """Khởi tạo database, tạo bảng và chèn dữ liệu mẫu."""
    # Xóa file db cũ nếu tồn tại
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Đã xóa database cũ: {DB_FILE}")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tạo bảng authors
    cursor.execute('''
        CREATE TABLE authors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    print("Đã tạo bảng 'authors'")

    # Tạo bảng books
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author_id INTEGER,
            FOREIGN KEY (author_id) REFERENCES authors (id)
        )
    ''')
    print("Đã tạo bảng 'books'")

    # Chèn dữ liệu mẫu
    authors_data = [
        (1, 'George Orwell'),
        (2, 'J.K. Rowling'),
        (3, 'J.R.R. Tolkien')
    ]
    cursor.executemany('INSERT INTO authors (id, name) VALUES (?, ?)', authors_data)
    print(f"Đã chèn {len(authors_data)} tác giả.")

    books_data = [
        (1, '1984', 1),
        (2, 'Animal Farm', 1),
        (3, 'Harry Potter and the Sorcerer\'s Stone', 2),
        (4, 'Harry Potter and the Chamber of Secrets', 2),
        (5, 'The Hobbit', 3),
        (6, 'The Lord of the Rings', 3)
    ]
    cursor.executemany('INSERT INTO books (id, title, author_id) VALUES (?, ?, ?)', books_data)
    print(f"Đã chèn {len(books_data)} cuốn sách.")

    conn.commit()
    conn.close()
    print("✓ Khởi tạo database thành công!")

if __name__ == '__main__':
    init_db()
