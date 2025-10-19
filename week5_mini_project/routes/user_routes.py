from flask import Blueprint, request, jsonify
from database import get_db
from models import User
import json

user_bp = Blueprint('users', __name__)

@user_bp.route('', methods=['GET'])
def get_users():
    """Lấy danh sách users"""
    status = request.args.get('status')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM users'
    params = []
    if status:
        query += ' WHERE status = ?'
        params.append(status)
    
    cursor.execute(query, params)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'count': len(users), 'data': users})

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Lấy user theo ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404
    
    return jsonify({'success': True, 'data': dict(user)})

@user_bp.route('', methods=['POST'])
def create_user():
    """Tạo user mới"""
    data = request.get_json()
    
    # Validate bằng User model
    is_valid, errors = User.validate(data)
    if not is_valid:
        return jsonify({'success': False, 'errors': errors}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Kiểm tra email trùng
    if cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],)).fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Email đã tồn tại'}), 400
    
    # Tạo user từ model
    user_data = User.create(data)
    
    cursor.execute('''
        INSERT INTO users (name, email, phone, address, status, borrowed_books)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_data['name'], user_data['email'], user_data['phone'],
          user_data['address'], user_data['status'], user_data['borrowed_books']))
    
    conn.commit()
    user_id = cursor.lastrowid
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    new_user = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({'success': True, 'message': 'Tạo người dùng thành công', 'data': new_user}), 201

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Cập nhật user"""
    data = request.get_json()
    
    is_valid, errors = User.validate(data)
    if not is_valid:
        return jsonify({'success': False, 'errors': errors}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404
    
    cursor.execute('''
        UPDATE users SET name=?, email=?, phone=?, address=?, status=? WHERE id=?
    ''', (data['name'], data['email'], data['phone'],
          data.get('address', ''), data.get('status', 'active'), user_id))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    updated_user = dict(cursor.fetchone())
    conn.close()
    
    return jsonify({'success': True, 'message': 'Cập nhật thành công', 'data': updated_user})

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Xóa user"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404
    
    # Kiểm tra bằng User model
    if User.has_borrowed_books(dict(user)):
        conn.close()
        return jsonify({'success': False, 'message': 'Không thể xóa người dùng đang mượn sách'}), 400
    
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Xóa người dùng thành công'})
