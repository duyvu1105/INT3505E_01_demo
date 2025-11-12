import connexion
import six

from swagger_server.models.auth_login_body import AuthLoginBody  # noqa: E501
from swagger_server.models.auth_refresh_body import AuthRefreshBody  # noqa: E501
from swagger_server.models.auth_register_body import AuthRegisterBody  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from swagger_server.models.inline_response201 import InlineResponse201  # noqa: E501
from swagger_server import util
from flask import request, jsonify
from datetime import datetime, timedelta

import jwt
from ..utils.auth_utils import JWT_REFRESH_EXPIRES_IN, JWT_EXPIRES_IN, JWT_SECRET

from ..utils.auth_utils import authenticate_token, require_admin, generate_token
from ..database.database import get_all_users, get_all_books_from_db, save_refresh_token, insert_new_user, get_refresh_token
users = get_all_users()
books = get_all_books_from_db()

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


def login(body):  # noqa: E501
    """Đăng nhập

    Đăng nhập và nhận JWT token # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse200
    """
    # 1. Lấy JSON từ request và validate
    if not connexion.request.is_json:
        return (
            {
                "success": False,
                "message": "Request body phải là JSON",
            },
            400,
        )
    
    data = AuthLoginBody.from_dict(connexion.request.get_json())  # noqa: E501
    username = data.username
    password = data.password
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
    )
    refresh_token = generate_token(
        {"id": user["id"], "username": user["username"], "role": user["role"], "type": "refresh"},
    )
    save_refresh_token(user["id"], refresh_token, datetime.utcnow() + JWT_REFRESH_EXPIRES_IN)
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


def refresh_token(body):  # noqa: E501
    """Cấp lại access token từ refresh token

    Nhận access token mới khi access token cũ hết hạn, sử dụng refresh token hợp lệ.  # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse2001
    """
    if not connexion.request.is_json:
        return (
            {
                "success": False,
                "message": "Request body phải là JSON",
            },
            400,
        )
    data = AuthRefreshBody.from_dict(connexion.request.get_json())  # noqa: E501
    refresh_token = data.refresh_token
    if not refresh_token:
        return jsonify({"success": False, "message": "Refresh token là bắt buộc"}), 400
    try:
        decoded = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
        if decoded.get("type") != "refresh":
            return jsonify({"success": False, "message": "Token không hợp lệ"}), 403
        user_id = decoded.get("id")
        # Kiểm tra refresh token có hợp lệ không (demo: so sánh với token đã cấp)
        if get_refresh_token(user_id, refresh_token)['token'] != refresh_token:
            return jsonify({"success": False, "message": "Refresh token không hợp lệ"}), 403
        # Cấp lại access token mới
        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            return jsonify({"success": False, "message": "Không tìm thấy user"}), 404
        access_token = generate_token(
            {"id": user["id"], "username": user["username"], "role": user["role"]},
        )
        return jsonify({"success": True, "access_token": access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Refresh token đã hết hạn"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Refresh token không hợp lệ"}), 403


def register(body):  # noqa: E501
    """Đăng ký tài khoản mới

    Tạo tài khoản người dùng mới trong hệ thống # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse201
    """
    if not connexion.request.is_json:
        return (
            {
                "success": False,
                "message": "Request body phải là JSON",
            },
            400,
        )
    data = AuthRegisterBody.from_dict(connexion.request.get_json())  # noqa: E501
    username = data.username
    password = data.password
    email = data.email
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
        "username": username,
        "password": password,  # CẢNH BÁO: Không bao giờ lưu plain password trong production
        "email": email,
        "role": "user",  # Mặc định là user thường
    }
    insert_new_user(username, password, email, "user")
    access_token = generate_token(
        {"username": new_user["username"], "role": new_user["role"]},
    )
    refresh_token = generate_token(
        {"username": new_user["username"], "role": new_user["role"], "type": "refresh"},
        expires_in=JWT_REFRESH_EXPIRES_IN,
    )
    save_refresh_token(new_user["username"], refresh_token, datetime.utcnow() + JWT_REFRESH_EXPIRES_IN)
    return (
        jsonify(
            {
                "success": True,
                "message": "Đăng ký thành công",
                "data": {
                    "user": {
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
