from flask import jsonify
from datetime import datetime

def get_users():
    """
    V2: Returns enhanced user information with metadata
    """
    return jsonify({
        'version': 'v2',
        'users': [
            {
                'id': 1,
                'name': 'Alice',
                'email': 'alice@example.com',
                'status': 'active',
                'created_at': '2024-01-15T10:00:00Z'
            },
            {
                'id': 2,
                'name': 'Bob',
                'email': 'bob@example.com',
                'status': 'active',
                'created_at': '2024-02-20T14:30:00Z'
            }
        ],
        'metadata': {
            'total': 2,
            'page': 1,
            'per_page': 10
        }
    })

def get_user(user_id):
    """
    V2: Returns enhanced user information by ID with additional details
    """
    users = {
        1: {
            'id': 1,
            'name': 'Alice',
            'email': 'alice@example.com',
            'status': 'active',
            'created_at': '2024-01-15T10:00:00Z',
            'profile': {
                'bio': 'Software Engineer',
                'location': 'San Francisco'
            }
        },
        2: {
            'id': 2,
            'name': 'Bob',
            'email': 'bob@example.com',
            'status': 'active',
            'created_at': '2024-02-20T14:30:00Z',
            'profile': {
                'bio': 'Product Manager',
                'location': 'New York'
            }
        }
    }
    
    user = users.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'version': 'v2',
        'user': user
    })

def create_payment(data):
    """
    V2: Enhanced payment processing with detailed response
    """
    payer = data.get('payer', {})
    
    return jsonify({
        'version': 'v2',
        'status': 'success',
        'payment': {
            'id': 'pay_67890',
            'amount': data.get('amount'),
            'currency': 'USD',
            'payer': {
                'name': payer.get('name'),
                'email': payer.get('email')
            },
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'pending'
        },
        'links': {
            'self': f'/api/payments/pay_67890',
            'confirm': f'/api/payments/pay_67890/confirm'
        }
    }), 201
