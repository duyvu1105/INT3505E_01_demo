"""
Payment API with URL-based versioning (v1 -> v2)
Demonstrating API versioning best practices
"""

from flask import Flask, jsonify, request
from datetime import datetime
import uuid

try:
    # When imported as a package (python -m week9_api_versioning.app)
    from .controllers.common import payments_db, api_keys, now_iso
    from .controllers.url_versioning.v1_controller import bp_v1
    from .controllers.url_versioning.v2_controller import bp_v2
    from .controllers.header_versioning import v1_controller as header_v1
    from .controllers.header_versioning import v2_controller as header_v2
except Exception:
    # When executed as a script (python week9_api_versioning/app.py)
    from controllers.common import payments_db, api_keys, now_iso
    from controllers.url_versioning.v1_controller import bp_v1
    from controllers.url_versioning.v2_controller import bp_v2
    from controllers.header_versioning import v1_controller as header_v1
    from controllers.header_versioning import v2_controller as header_v2

app = Flask(__name__)

# Register blueprints for URL versioning (v1 and v2)
app.register_blueprint(bp_v1, url_prefix='/api/v1')
app.register_blueprint(bp_v2, url_prefix='/api/v2')


# Header-based versioning routes
@app.route('/api/users', methods=['GET'])
def header_get_users():
    """Get users with header-based versioning"""
    version = request.headers.get('API-Version', 'v1')
    
    if version == 'v2':
        return header_v2.get_users()
    else:
        return header_v1.get_users()


@app.route('/api/users/<int:user_id>', methods=['GET'])
def header_get_user(user_id):
    """Get user by ID with header-based versioning"""
    version = request.headers.get('API-Version', 'v1')
    
    if version == 'v2':
        return header_v2.get_user(user_id)
    else:
        return header_v1.get_user(user_id)


@app.route('/api/payments', methods=['POST'])
def header_create_payment():
    """Create payment with header-based versioning"""
    version = request.headers.get('API-Version', 'v1')
    data = request.get_json() or {}
    
    if version == 'v2':
        return header_v2.create_payment(data)
    else:
        return header_v1.create_payment(data)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "versions": {
            "v1": "deprecated",
            "v2": "active"
        }
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Payment API Server Starting...")
    print("="*70)
    print("\nURL-based Versioning:")
    print("  - V1 (DEPRECATED): http://localhost:5000/api/v1/payments")
    print("    Auth: X-API-Key: test_key_v1")
    print("  - V2 (CURRENT):    http://localhost:5000/api/v2/payments")
    print("    Auth: Authorization: Bearer test_token_v2")
    print("\nHeader-based Versioning:")
    print("  - Endpoint:        http://localhost:5000/api/users")
    print("  - Endpoint:        http://localhost:5000/api/payments")
    print("  - V1 Header:       API-Version: v1 (default)")
    print("  - V2 Header:       API-Version: v2")
    print("\nHealth Check:        http://localhost:5000/health")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000)
