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
    from .controllers.v1_controller import bp_v1
    from .controllers.v2_controller import bp_v2
except Exception:
    # When executed as a script (python week9_api_versioning/app.py)
    from controllers.common import payments_db, api_keys, now_iso
    from controllers.v1_controller import bp_v1
    from controllers.v2_controller import bp_v2

app = Flask(__name__)

# Register blueprints for v1 and v2
app.register_blueprint(bp_v1, url_prefix='/api/v1')
app.register_blueprint(bp_v2, url_prefix='/api/v2')


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
    print("\nAPI Versions:")
    print("  - V1 (DEPRECATED): http://localhost:5000/api/v1/payments")
    print("    Auth: X-API-Key: test_key_v1")
    print("  - V2 (CURRENT):    http://localhost:5000/api/v2/payments")
    print("    Auth: Authorization: Bearer test_token_v2")
    print("  - Health Check:    http://localhost:5000/health")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000)
