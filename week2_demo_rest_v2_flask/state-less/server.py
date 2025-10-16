from flask import Flask, jsonify, request
from functools import wraps
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'my-secret-key-2025'
app = Flask(__name__)

# Users database
users = [
    {'id': 1, 'username': 'admin', 'password': '123', 'role': 'admin'},
    {'id': 2, 'username': 'user', 'password': '123', 'role': 'user'}
]

# Sample data
items = [
    {'id': 1, 'name': 'Item 1'},
    {'id': 2, 'name': 'Item 2'},
]

# Stateless: Mỗi request là độc lập
# Server không cần lưu trạng thái giữa các request


def authenticate_token(f):
    """Decorator to verify JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            # Extract token from "Bearer TOKEN"
            token = auth_header.split(' ')[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = decoded
            print(f'Authenticated user: {decoded["username"]}')
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 403
    
    return decorated_function


@app.route('/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    print(f'Login attempt: {username}')
    
    # Find user
    user = next((u for u in users if u['username'] == username and u['password'] == password), None)
    
    if not user:
        print('Invalid credentials')
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create JWT token
    token = jwt.encode(
        {
            'userId': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        SECRET_KEY,
        algorithm='HS256'
    )
    
    print(f'Login successful for: {user["username"]}')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        },
        'expiresIn': 3600
    })


@app.route('/items', methods=['GET'])
def get_items():
    """Get all items (no auth required)"""
    return jsonify(items)


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get single item (no auth required)"""
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify(item)


@app.route('/items', methods=['POST'])
@authenticate_token
def create_item():
    """Create new item (auth required)"""
    data = request.get_json()
    new_item = {
        'id': len(items) + 1,
        'name': data.get('name')
    }
    items.append(new_item)
    return jsonify(new_item), 201


@app.route('/items/<int:item_id>', methods=['PUT'])
@authenticate_token
def update_item(item_id):
    """Update item (auth required)"""
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    item['name'] = data.get('name')
    return jsonify(item)


@app.route('/items/<int:item_id>', methods=['DELETE'])
@authenticate_token
def delete_item(item_id):
    """Delete item (admin only)"""
    # Check if user is admin
    if request.user.get('role') != 'admin':
        return jsonify({'error': 'Forbidden: Admins only'}), 403
    
    global items
    item_index = next((i for i, item in enumerate(items) if item['id'] == item_id), None)
    if item_index is None:
        return jsonify({'error': 'Item not found'}), 404
    
    items.pop(item_index)
    return '', 204


if __name__ == '__main__':
    print('Server is running on http://localhost:5000')
    app.run(debug=True, port=5000)
