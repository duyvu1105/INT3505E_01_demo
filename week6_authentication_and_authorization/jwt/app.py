from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Cấu hình JWT
JWT_SECRET = "your-secret-key-change-this-in-production"

# JWT cấu hình
JWT_EXPIRES_IN = timedelta(minutes=1)
JWT_REFRESH_EXPIRES_IN = timedelta(days=7)

# Lưu refresh token tạm thời (demo, production nên lưu DB hoặc Redis)
refresh_tokens = {}

# Database giả lập cho sách
books = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "year": 2008,
        "price": 45.99,
    },
    {
        "id": 2,
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "year": 1999,
        "price": 42.5,
    },
    {
        "id": 3,
        "title": "Design Patterns",
        "author": "Gang of Four",
        "year": 1994,
        "price": 54.99,
    },
]

next_book_id = 4

# Database giả lập cho users
users = [
    {
        "id": 1,
        "username": "admin",
        "password": "admin123",  # Trong thực tế nên hash password
        "email": "admin@example.com",
        "role": "admin",
    },
    {
        "id": 2,
        "username": "user",
        "password": "user123",
        "email": "user@example.com",
        "role": "user",
    },
]

next_user_id = 3


# ============= JWT UTILITIES =============

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


# ============= SWAGGER UI CONFIGURATION =============
SWAGGER_URL = "/api-docs"
API_URL = "/books-api.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Books API Documentation",
        "docExpansion": "list",
        "defaultModelsExpandDepth": 3,
    },
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# ============= AUTHENTICATION ROUTES =============
@app.route("/api/auth/register", methods=["POST"])
def register():
    """Đăng ký user mới"""
    global next_user_id

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    # Validation
    if not username or not password or not email:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Username, password và email là bắt buộc",
                }
            ),
            400,
        )

    # Kiểm tra username đã tồn tại
    if any(u["username"] == username for u in users):
        return (
            jsonify({"success": False, "message": "Username đã tồn tại"}),
            400,
        )

    # Tạo user mới (trong thực tế nên hash password)
    new_user = {
        "id": next_user_id,
        "username": username,
        "password": password,  # CẢNH BÁO: Không bao giờ lưu plain password trong production
        "email": email,
        "role": "user",  # Mặc định là user thường
    }

    users.append(new_user)
    next_user_id += 1

    # Tạo JWT token và refresh token
    access_token = generate_token(
        {"id": new_user["id"], "username": new_user["username"], "role": new_user["role"]},
        expires_in=JWT_EXPIRES_IN,
    )
    refresh_token = generate_token(
        {"id": new_user["id"], "username": new_user["username"], "role": new_user["role"], "type": "refresh"},
        expires_in=JWT_REFRESH_EXPIRES_IN,
    )
    refresh_tokens[new_user["id"]] = refresh_token

    return (
        jsonify(
            {
                "success": True,
                "message": "Đăng ký thành công",
                "data": {
                    "user": {
                        "id": new_user["id"],
                        "username": new_user["username"],
                        "email": new_user["email"],
                        "role": new_user["role"],
                    },
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
        ),
        201,
    )


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Đăng nhập"""
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # Validation
    if not username or not password:
        return (
            jsonify(
                {"success": False, "message": "Username và password là bắt buộc"}
            ),
            400,
        )

    # Tìm user
    user = next(
        (u for u in users if u["username"] == username and u["password"] == password),
        None,
    )

    if not user:
        return (
            jsonify(
                {"success": False, "message": "Username hoặc password không đúng"}
            ),
            401,
        )

    # Tạo JWT token và refresh token
    access_token = generate_token(
        {"id": user["id"], "username": user["username"], "role": user["role"]},
        expires_in=JWT_EXPIRES_IN,
    )
    refresh_token = generate_token(
        {"id": user["id"], "username": user["username"], "role": user["role"], "type": "refresh"},
        expires_in=JWT_REFRESH_EXPIRES_IN,
    )
    refresh_tokens[user["id"]] = refresh_token

    return jsonify(
        {
            "success": True,
            "message": "Đăng nhập thành công",
            "data": {
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        }
    )

# ============= REFRESH TOKEN ROUTE =============
@app.route("/api/auth/refresh", methods=["POST"])
def refresh_access_token():
    """Cấp lại access token từ refresh token"""
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token là bắt buộc"}), 400
    try:
        decoded = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
        if decoded.get("type") != "refresh":
            return jsonify({"success": False, "message": "Token không hợp lệ"}), 403
        user_id = decoded.get("id")
        # Kiểm tra refresh token có hợp lệ không (demo: so sánh với token đã cấp)
        if refresh_tokens.get(user_id) != refresh_token:
            return jsonify({"success": False, "message": "Refresh token không hợp lệ"}), 403
        # Cấp lại access token mới
        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            return jsonify({"success": False, "message": "Không tìm thấy user"}), 404
        access_token = generate_token(
            {"id": user["id"], "username": user["username"], "role": user["role"]},
            expires_in=JWT_EXPIRES_IN,
        )
        return jsonify({"success": True, "access_token": access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Refresh token đã hết hạn"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Refresh token không hợp lệ"}), 403


@app.route("/api/auth/me", methods=["GET"])
@authenticate_token
def get_current_user():
    """Lấy thông tin user hiện tại (cần token)"""
    user = next((u for u in users if u["id"] == request.user["id"]), None)

    if not user:
        return jsonify({"success": False, "message": "Không tìm thấy user"}), 404

    return jsonify(
        {
            "success": True,
            "data": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
            },
        }
    )


# ============= BOOKS ROUTES =============
@app.route("/api/books", methods=["GET"])
def get_all_books():
    """Lấy tất cả sách (KHÔNG yêu cầu xác thực)"""
    return jsonify({"success": True, "data": books})


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):
    """Lấy sách theo ID"""
    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        return jsonify({"success": False, "message": "Không tìm thấy sách"}), 404

    return jsonify({"success": True, "data": book})


@app.route("/api/books", methods=["POST"])
@authenticate_token
def create_book():
    """Tạo sách mới (YÊU CẦU xác thực)"""
    global next_book_id

    data = request.get_json()

    title = data.get("title")
    author = data.get("author")
    year = data.get("year", datetime.now().year)
    price = data.get("price", 0)

    # Validation
    if not title or not author:
        return (
            jsonify({"success": False, "message": "Title và Author là bắt buộc"}),
            400,
        )

    new_book = {
        "id": next_book_id,
        "title": title,
        "author": author,
        "year": year,
        "price": price,
    }

    books.append(new_book)
    next_book_id += 1

    return jsonify({"success": True, "data": new_book}), 201


@app.route("/api/books/<int:book_id>", methods=["PUT"])
@authenticate_token
def update_book(book_id):
    """Cập nhật sách (YÊU CẦU xác thực)"""
    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        return jsonify({"success": False, "message": "Không tìm thấy sách"}), 404

    data = request.get_json()

    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return (
            jsonify({"success": False, "message": "Title và Author là bắt buộc"}),
            400,
        )

    book["title"] = title
    book["author"] = author
    book["year"] = data.get("year", book["year"])
    book["price"] = data.get("price", book["price"])

    return jsonify({"success": True, "data": book})


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
@authenticate_token
@require_admin
def delete_book(book_id):
    """Xóa sách (YÊU CẦU xác thực)"""
    global books

    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        return jsonify({"success": False, "message": "Không tìm thấy sách"}), 404

    books = [b for b in books if b["id"] != book_id]

    return jsonify({"success": True, "message": "Xóa sách thành công"})


# ============= STATIC FILES =============
@app.route("/books-api.yaml")
def serve_yaml():
    """Serve YAML file"""
    return send_from_directory(".", "books-api.yaml")


@app.route("/")
def index():
    """Redirect to API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/api-docs">
    </head>
    <body>
        <p>Redirecting to <a href="/api-docs">API Documentation</a>...</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    print("Server đang chạy tại: http://localhost:3000")
    print("API endpoint: http://localhost:3000/api/books")
    print("Swagger UI (API Docs): http://localhost:3000/api-docs")
    print("OpenAPI YAML: http://localhost:3000/books-api.yaml")
    app.run(debug=True, port=3000)
