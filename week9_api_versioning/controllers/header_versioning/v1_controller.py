from flask import jsonify

def get_users():
    """
    V1: Returns basic user information
    """
    return jsonify({
        'version': 'v1',
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    })

def get_user(user_id):
    """
    V1: Returns basic user information by ID
    """
    users = {
        1: {'id': 1, 'name': 'Alice'},
        2: {'id': 2, 'name': 'Bob'}
    }
    
    user = users.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'version': 'v1',
        'user': user
    })

def create_payment(data):
    """
    V1: Simple payment processing
    """
    return jsonify({
        'version': 'v1',
        'status': 'success',
        'payment_id': 'pay_12345',
        'amount': data.get('amount')
    }), 201
