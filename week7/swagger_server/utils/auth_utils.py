from functools import wraps
import jwt
from datetime import datetime, timedelta
JWT_SECRET = "your-secret-key-change-this-in-production"

# JWT cấu hình
JWT_EXPIRES_IN = timedelta(minutes=30)
JWT_REFRESH_EXPIRES_IN = timedelta(days=7)
from flask import request, jsonify

def generate_token(payload, expires_in=JWT_EXPIRES_IN):
    """Tạo JWT token với thời hạn tùy chọn"""
    payload = payload.copy()
    payload["exp"] = datetime.utcnow() + expires_in
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def authenticate_token(f):
    """Decorator để xác thực JWT token"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return (
                jsonify({"success": False, "message": "Token không được cung cấp"}),
                401,
            )

        try:
            # Format: "Bearer TOKEN"
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header

            # Xác thực token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = decoded

        except jwt.ExpiredSignatureError:
            return (
                jsonify(
                    {"success": False, "message": "Token đã hết hạn"}
                ),
                403,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify(
                    {"success": False, "message": "Token không hợp lệ"}
                ),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """Decorator kiểm tra quyền admin (optional)"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, "user") or request.user.get("role") != "admin":
            return (
                jsonify({"success": False, "message": "Bạn không có quyền truy cập"}),
                403,
            )
        return f(*args, **kwargs)

    return decorated_function
