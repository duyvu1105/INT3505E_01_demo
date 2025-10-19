import sqlite3

DATABASE = 'library.db'

def get_db():
    """Kết nối database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Khởi tạo database với schema và dữ liệu mẫu"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Drop tables nếu tồn tại
    cursor.execute('DROP TABLE IF EXISTS borrowings')
    cursor.execute('DROP TABLE IF EXISTS books')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # Tạo bảng Books
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            published_year INTEGER,
            category TEXT DEFAULT 'Uncategorized',
            quantity INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1
        )
    ''')
    
    # Tạo bảng Users
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            status TEXT DEFAULT 'active',
            borrowed_books TEXT DEFAULT '[]'
        )
    ''')
    
    # Tạo bảng Borrowings
    cursor.execute('''
        CREATE TABLE borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT DEFAULT 'borrowed',
            fine REAL DEFAULT 0
        )
    ''')
    
    # Insert dữ liệu mẫu - Books
    sample_books = [
        ('Clean Code', 'Robert C. Martin', '9780132350884', 2008, 'Programming', 5, 5),
        ('The Pragmatic Programmer', 'Andrew Hunt, David Thomas', '9780201616224', 1999, 'Programming', 3, 3),
        ('Design Patterns', 'Gang of Four', '9780201633610', 1994, 'Programming', 4, 4),
        ('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 2009, 'Algorithms', 2, 2),
        ('JavaScript: The Good Parts', 'Douglas Crockford', '9780596517748', 2008, 'Programming', 6, 6),
    ]
    
    cursor.executemany('''
        INSERT INTO books (title, author, isbn, published_year, category, quantity, available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_books)
    
    # Insert dữ liệu mẫu - Users
    sample_users = [
        ('Nguyễn Văn A', 'nguyenvana@example.com', '0123456789', 'Hà Nội', 'active', '[]'),
        ('Trần Thị B', 'tranthib@example.com', '0987654321', 'TP. HCM', 'active', '[]'),
    ]
    
    cursor.executemany('''
        INSERT INTO users (name, email, phone, address, status, borrowed_books)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_users)
    
    conn.commit()
    conn.close()
    
    print('✓ Database initialized successfully!')
