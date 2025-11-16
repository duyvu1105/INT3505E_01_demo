from flask import Blueprint, jsonify, request
import uuid

from .common import payments_db, api_keys, now_iso

bp_v1 = Blueprint('v1_payments', __name__)


def verify_api_key_v1():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in api_keys:
        return None
    return api_keys[api_key]


@bp_v1.route('/payments', methods=['POST'])
def create_payment_v1():
    response_headers = {
        'Deprecation': 'true',
        'Sunset': 'Sun, 15 Feb 2026 00:00:00 GMT',
        'Link': '<http://localhost:5000/docs/migrate-v2>; rel="migration"',
        'Warning': '299 - "API v1 is deprecated. Please migrate to /api/v2/payments"'
    }
    user = verify_api_key_v1()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401, response_headers

    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({"error": "Missing amount"}), 400, response_headers

    payment_id = str(uuid.uuid4())
    payment = {
        "id": payment_id,
        "amount": data['amount'],
        "currency": data.get('currency', 'USD'),
        "customer_email": data.get('customer_email'),
        "status": "pending",
        "created_at": now_iso()
    }
    payments_db[payment_id] = payment

    return jsonify({
        "success": True,
        "payment_id": payment_id,
        "amount": payment['amount'],
        "status": payment['status']
    }), 201, response_headers


@bp_v1.route('/payments/<payment_id>', methods=['GET'])
def get_payment_v1(payment_id):
    response_headers = {
        'Deprecation': 'true',
        'Sunset': 'Sun, 15 Feb 2026 00:00:00 GMT',
        'Link': '<http://localhost:5000/docs/migrate-v2>; rel="migration"',
        'Warning': '299 - "API v1 is deprecated. Please migrate to /api/v2/payments"'
    }
    user = verify_api_key_v1()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401, response_headers

    payment = payments_db.get(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404, response_headers

    return jsonify({"success": True, "payment": payment}), 200, response_headers


@bp_v1.route('/payments', methods=['GET'])
def list_payments_v1():
    response_headers = {
        'Deprecation': 'true',
        'Sunset': 'Sun, 15 Feb 2026 00:00:00 GMT',
        'Link': '<http://localhost:5000/docs/migrate-v2>; rel="migration"',
        'Warning': '299 - "API v1 is deprecated. Please migrate to /api/v2/payments"'
    }
    user = verify_api_key_v1()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401, response_headers

    return jsonify({"success": True, "payments": list(payments_db.values())}), 200, response_headers
