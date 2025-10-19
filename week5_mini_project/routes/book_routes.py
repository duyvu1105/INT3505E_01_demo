from flask import Blueprint, request, jsonify
from database import get_db
from models import Book
import json
import base64

book_bp = Blueprint('books', __name__)

# page-based pagination : localhost:3000/api/books?category=Fiction&page=1&limit=5
@book_bp.route('', methods=['GET'])
def get_books():
    """Lấy danh sách sách với filter và pagination"""
    category = request.args.get('category')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM books'
    params = []
    
    if category:
        query += ' WHERE category = ?'
        params.append(category)
    
    # Pagination
    offset = (page - 1) * limit
    query += f' LIMIT {limit} OFFSET {offset}'
    
    cursor.execute(query, params)
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'count': len(books), 'data': books})

# offset-limit pagination : localhost:3000/api/books/v2?category=Fiction&offset=0&limit=5
@book_bp.route('v2', methods=['GET'])
def get_books_v2():
    """Lấy danh sách sách với filter và offset-limit pagination"""
    category = request.args.get('category')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM books'
    params = []
    
    if category:
        query += ' WHERE category = ?'
        params.append(category)
    
    # Offset-Limit Pagination
    query += f' LIMIT {limit} OFFSET {offset}'
    
    cursor.execute(query, params)
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'count': len(books), 'data': books})

def encode_cursor(data):
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()

def decode_cursor(cursor_str):
    json_str = base64.b64decode(cursor_str.encode()).decode()
    return json.loads(json_str)

#cursor based pagination : localhost:3000/api/books/v3?limit=5&cursor=5
@book_bp.route('v3', methods=['GET'])
def get_books_v3():
    """Cursor pagination với Base64 encoding"""
    
    limit = int(request.args.get('limit', 10))
    cursor_param = request.args.get('cursor')

    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    
    # Decode cursor
    if cursor_param:
        cursor_data = decode_cursor(cursor_param)
        if cursor_data['direction'] == 'next':
            if cursor_data and 'last_id' in cursor_data:
                query += ' AND id > ?'
                params.append(cursor_data['last_id'])
            query += ' ORDER BY id ASC LIMIT ?'
        elif cursor_data['direction'] == 'prev':
            if cursor_data and 'first_id' in cursor_data:
                query += ' AND id < ?'
                params.append(cursor_data['first_id'])
            query += ' ORDER BY id DESC LIMIT ?'

    
    params.append(limit)
    
    cursor.execute(query, params)
    books = [dict(row) for row in cursor.fetchall()]
    
    if cursor_data['direction'] == 'prev':
        books.reverse()
    
    # Tạo cursors theo logic chuẩn
    next_cursor = None
    prev_cursor = None
    
    if books:
        first_book = books[0]
        last_book = books[-1]
        
        if len(books) == limit:
            next_cursor = encode_cursor({
                'last_id': last_book['id'],
                'direction': 'next'
            })

        if first_book['id'] > 1:
            prev_cursor = encode_cursor({
                'first_id': first_book['id'],
                'direction': 'prev'
            })
    
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(books),
        'data': books,
        'next_cursor': next_cursor,  # Trả về next cursor đã mã hóa
        'prev_cursor': prev_cursor  # Trả về prev cursor đã mã hóa
    })


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Lấy sách theo ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    conn.close()
    
    if not book:
        return jsonify({'success': False, 'message': 'Không tìm thấy sách'}), 404
    
    return jsonify({'success': True, 'data': dict(book)})

@book_bp.route('', methods=['POST'])
def create_book():
    """Tạo sách mới"""
    data = request.get_json()
    
    # Validate bằng Book model
    is_valid, errors = Book.validate(data)
    if not is_valid:
        return jsonify({'success': False, 'errors': errors}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Kiểm tra ISBN trùng
    if cursor.execute('SELECT id FROM books WHERE isbn = ?', (data['isbn'],)).fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'ISBN đã tồn tại'}), 400
    
    # Tạo book từ model
    book_data = Book.create(data)
    
    cursor.execute('''
        INSERT INTO books (title, author, isbn, published_year, category, quantity, available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (book_data['title'], book_data['author'], book_data['isbn'],
          book_data['published_year'], book_data['category'], 
          book_data['quantity'], book_data['available']))
    
    conn.commit()
    book_id = cursor.lastrowid
    
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    new_book = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({'success': True, 'message': 'Tạo sách thành công', 'data': new_book}), 201

@book_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Cập nhật sách"""
    data = request.get_json()
    
    # Validate
    is_valid, errors = Book.validate(data)
    if not is_valid:
        return jsonify({'success': False, 'errors': errors}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy sách'}), 404
    
    # Tính số sách đang được mượn
    book_dict = dict(book)
    borrowed = Book.get_borrowed_count(book_dict)
    
    cursor.execute('''
        UPDATE books 
        SET title=?, author=?, isbn=?, published_year=?, category=?, quantity=?, available=?
        WHERE id = ?
    ''', (data['title'], data['author'], data['isbn'],
          data.get('published_year'), data.get('category'),
          data.get('quantity', book_dict['quantity']),
          data.get('quantity', book_dict['quantity']) - borrowed,
          book_id))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    updated_book = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({'success': True, 'message': 'Cập nhật thành công', 'data': updated_book})

@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Xóa sách"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    
    if not book:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy sách'}), 404
    
    # Kiểm tra bằng Book model
    if Book.has_borrowed_books(dict(book)):
        conn.close()
        return jsonify({'success': False, 'message': 'Không thể xóa sách đang được mượn'}), 400
    
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Xóa sách thành công'})

@book_bp.route('/search', methods=['GET'])
def search_books():
    """Tìm kiếm sách nâng cao"""
    q = request.args.get('q')
    title = request.args.get('title')
    author = request.args.get('author')
    category = request.args.get('category')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    
    if q:
        query += ''' AND (
            LOWER(title) LIKE LOWER(?) OR 
            LOWER(author) LIKE LOWER(?) OR 
            LOWER(category) LIKE LOWER(?)
        )'''
        search_term = f'%{q}%'
        params.extend([search_term, search_term, search_term])
    
    if title:
        query += ' AND LOWER(title) LIKE LOWER(?)'
        params.append(f'%{title}%')
    
    if author:
        query += ' AND LOWER(author) LIKE LOWER(?)'
        params.append(f'%{author}%')
    
    if category:
        query += ' AND LOWER(category) = LOWER(?)'
        params.append(category)
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(results),
        'data': results
    })
