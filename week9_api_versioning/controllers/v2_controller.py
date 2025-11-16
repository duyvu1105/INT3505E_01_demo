from flask import Blueprint, jsonify, request
import uuid

from .common import payments_db, api_keys, now_iso

bp_v2 = Blueprint('v2_payments', __name__)


def verify_bearer_token_v2():
    """V2 authentication: Bearer token (OAuth2-style)"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    if token not in api_keys:
        return None
    return api_keys[token]


@bp_v2.route('/payments', methods=['POST'])
def create_payment_v2():
    """
    Use ?format=extended query param to get additional fields in response
    """
    user = verify_bearer_token_v2()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    data = request.get_json() or {}
    
    amount = None
    if 'amount' in data:
        if not isinstance(data['amount'], int):
            return jsonify({
                "error": {
                    "type": "invalid_request",
                    "message": "amount must be an integer"
                }
            }), 400
        amount = data['amount']
    else:
        return jsonify({
            "error": {
                "type": "invalid_request",
                "message": "Either amount or amount is required"
            }
        }), 400

    # Currency is optional (default USD for backward compatibility)
    currency = data.get('currency', 'USD')
    
    # Support both old (customer_email) and new (payer.email) format
    email = None
    if 'payer' in data and isinstance(data['payer'], dict):
        email = data['payer'].get('email')
    elif 'customer_email' in data:
        email = data['customer_email']
    
    if not email:
        return jsonify({
            "error": {
                "type": "invalid_request",
                "message": "Email is required (use payer.email or customer_email)"
            }
        }), 400

    payment_id = str(uuid.uuid4())
    
    # Store in new format internally
    payment = {
        "id": payment_id,
        "amount": amount,
        "currency": currency,
        "payer": {
            "email": email,
            "name": data.get('payer', {}).get('name') if isinstance(data.get('payer'), dict) else None
        },
        "status": "pending",
        "created_at": now_iso()
    }
    
    # Store optional metadata if provided
    if 'metadata' in data:
        payment['metadata'] = data['metadata']
    
    payments_db[payment_id] = payment

    # Use query param ?format=extended to get new response format
    response_format = request.args.get('format', 'standard')
    
    if response_format == 'extended':
        # New format: full envelope with metadata
        return jsonify({
            "data": payment,
            "meta": {"version": "v2", "request_id": str(uuid.uuid4())}
        }), 201
    else:
        # Standard format: backward compatible with V1 style
        return jsonify({
            "success": True,
            "payment_id": payment_id,
            "amount": payment['amount'],
            "status": payment['status']
        }), 201


@bp_v2.route('/payments/<payment_id>', methods=['GET'])
def get_payment_v2(payment_id):
    """
    Get payment by ID
    Use ?format=extended for full envelope response
    """
    user = verify_bearer_token_v2()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    payment = payments_db.get(payment_id)
    if not payment:
        return jsonify({
            "error": {
                "type": "not_found",
                "message": "Payment not found"
            }
        }), 404

    # Use query param for response format control
    response_format = request.args.get('format', 'standard')
    
    if response_format == 'extended':
        return jsonify({"data": payment, "meta": {"version": "v2"}}), 200
    else:
        # Backward compatible format
        return jsonify({
            "success": True,
            "payment": payment
        }), 200


@bp_v2.route('/payments', methods=['GET'])
def list_payments_v2():
    """
    List payments
    Use ?format=extended for envelope + pagination
    Use ?limit=N&offset=M for pagination (only with format=extended)
    """
    user = verify_bearer_token_v2()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    response_format = request.args.get('format', 'standard')
    
    if response_format == 'extended':
        # New format with pagination
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        all_payments = list(payments_db.values())
        paginated = all_payments[offset:offset + limit]
        
        return jsonify({
            "data": paginated,
            "meta": {
                "version": "v2",
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(all_payments),
                    "has_more": offset + limit < len(all_payments)
                }
            }
        }), 200
    else:
        # Backward compatible format (no pagination)
        return jsonify({
            "success": True,
            "payments": list(payments_db.values())
        }), 200


@bp_v2.route('/payments/<payment_id>', methods=['PATCH'])
def update_payment_v2(payment_id):
    """
    Update payment (partial update)
    Use ?format=extended for envelope response
    """
    user = verify_bearer_token_v2()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    payment = payments_db.get(payment_id)
    if not payment:
        return jsonify({
            "error": {
                "type": "not_found",
                "message": "Payment not found"
            }
        }), 404

    data = request.get_json() or {}
    # Allow updating status and metadata
    if 'status' in data:
        payment['status'] = data['status']
    if 'metadata' in data:
        payment['metadata'] = data.get('metadata', {})
    
    payment['updated_at'] = now_iso()
    payments_db[payment_id] = payment

    response_format = request.args.get('format', 'standard')
    
    if response_format == 'extended':
        return jsonify({"data": payment, "meta": {"version": "v2"}}), 200
    else:
        # Backward compatible format
        return jsonify({
            "success": True,
            "payment": payment
        }), 200
