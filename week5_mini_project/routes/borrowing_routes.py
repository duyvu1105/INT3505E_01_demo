from flask import Blueprint, request, jsonify
from database import get_db
from models import Borrowing, Book, User
from datetime import datetime
import json

borrowing_bp = Blueprint('borrowings', __name__)

@borrowing_bp.route('', methods=['GET'])
def get_borrowings():
    """Lấy danh sách mượn sách"""
    status = request.args.get('status')
    user_id = request.args.get('userId')
    book_id = request.args.get('bookId')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM borrowings WHERE 1=1'
    params = []
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    if user_id:
        query += ' AND user_id = ?'
        params.append(int(user_id))
    if book_id:
        query += ' AND book_id = ?'
        params.append(int(book_id))
    
    cursor.execute(query, params)
    borrowings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'count': len(borrowings), 'data': borrowings})

@borrowing_bp.route('/<int:borrowing_id>', methods=['GET'])
def get_borrowing(borrowing_id):
    """Lấy phiếu mượn theo ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM borrowings WHERE id = ?', (borrowing_id,))
    borrowing = cursor.fetchone()
    conn.close()
    
    if not borrowing:
        return jsonify({'success': False, 'message': 'Không tìm thấy phiếu mượn'}), 404
    
    return jsonify({'success': True, 'data': dict(borrowing)})

@borrowing_bp.route('', methods=['POST'])
def create_borrowing():
    """Mượn sách"""
    data = request.get_json()
    
    # Validate
    is_valid, errors = Borrowing.validate(data)
    if not is_valid:
        return jsonify({'success': False, 'errors': errors}), 400
    
    user_id = int(data['user_id'])
    book_id = int(data['book_id'])
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Kiểm tra user
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404
    
    user_dict = dict(user)
    
    # Kiểm tra user có thể mượn không (dùng User model)
    if not User.can_borrow(user_dict):
        conn.close()
        if not User.is_active(user_dict):
            return jsonify({'success': False, 'message': 'Tài khoản không active'}), 400
        return jsonify({'success': False, 'message': 'Đã mượn tối đa 5 quyển'}), 400
    
    # Kiểm tra book
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy sách'}), 404
    
    book_dict = dict(book)
    
    # Kiểm tra sách còn không (dùng Book model)
    if not Book.is_available(book_dict):
        conn.close()
        return jsonify({'success': False, 'message': 'Sách không còn'}), 400
    
    # Tạo borrowing từ model
    borrowing_data = Borrowing.create(data)
    
    cursor.execute('''
        INSERT INTO borrowings (user_id, book_id, borrow_date, due_date, status, fine)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (borrowing_data['user_id'], borrowing_data['book_id'],
          borrowing_data['borrow_date'], borrowing_data['due_date'],
          borrowing_data['status'], borrowing_data['fine']))
    
    borrowing_id = cursor.lastrowid
    
    # Cập nhật book available
    cursor.execute('UPDATE books SET available = available - 1 WHERE id = ?', (book_id,))
    
    # Cập nhật user borrowed_books
    borrowed = json.loads(user_dict['borrowed_books'])
    borrowed.append(book_id)
    cursor.execute('UPDATE users SET borrowed_books = ? WHERE id = ?', 
                   (json.dumps(borrowed), user_id))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM borrowings WHERE id = ?', (borrowing_id,))
    new_borrowing = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({'success': True, 'message': 'Mượn sách thành công', 'data': new_borrowing}), 201

@borrowing_bp.route('/<int:borrowing_id>/return', methods=['PATCH'])
def return_book(borrowing_id):
    """Trả sách"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM borrowings WHERE id = ?', (borrowing_id,))
    borrowing = cursor.fetchone()
    
    if not borrowing:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy phiếu mượn'}), 404
    
    borrowing_dict = dict(borrowing)
    
    if borrowing_dict['status'] == 'returned':
        conn.close()
        return jsonify({'success': False, 'message': 'Sách đã được trả'}), 400
    
    # Tính phí phạt bằng Borrowing model
    return_date = datetime.now().strftime('%Y-%m-%d')
    fine = Borrowing.calculate_fine(borrowing_dict, return_date)
    
    # Cập nhật borrowing
    cursor.execute('''
        UPDATE borrowings SET return_date=?, status='returned', fine=? WHERE id=?
    ''', (return_date, fine, borrowing_id))
    
    # Cập nhật book available
    cursor.execute('UPDATE books SET available = available + 1 WHERE id = ?', 
                   (borrowing_dict['book_id'],))
    
    # Cập nhật user borrowed_books
    cursor.execute('SELECT borrowed_books FROM users WHERE id = ?', 
                   (borrowing_dict['user_id'],))
    user = cursor.fetchone()
    borrowed = json.loads(user['borrowed_books'])
    if borrowing_dict['book_id'] in borrowed:
        borrowed.remove(borrowing_dict['book_id'])
    cursor.execute('UPDATE users SET borrowed_books = ? WHERE id = ?',
                   (json.dumps(borrowed), borrowing_dict['user_id']))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM borrowings WHERE id = ?', (borrowing_id,))
    updated = dict(cursor.fetchone())
    conn.close()
    
    message = 'Trả sách thành công'
    if fine > 0:
        message = f'Trả sách thành công. Phí phạt: {int(fine):,} VNĐ'
    
    return jsonify({'success': True, 'message': message, 'data': updated})

@borrowing_bp.route('/overdue', methods=['GET'])
def get_overdue_borrowings():
    """Lấy danh sách quá hạn"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM borrowings WHERE status = ? AND due_date < ?', 
                   ('borrowed', today))
    overdue = [dict(row) for row in cursor.fetchall()]
    
    # Cập nhật status bằng Borrowing model
    for b in overdue:
        updated = Borrowing.update_overdue_status(b)
        cursor.execute('UPDATE borrowings SET status=?, fine=? WHERE id=?',
                       (updated['status'], updated['fine'], b['id']))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM borrowings WHERE status IN (?, ?) AND due_date < ?',
                   ('borrowed', 'overdue', today))
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'count': len(result), 'data': result})
