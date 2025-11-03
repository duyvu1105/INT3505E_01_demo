import connexion
import six

from swagger_server.models.book_input import BookInput  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from swagger_server.models.inline_response2004 import InlineResponse2004  # noqa: E501
from swagger_server.models.inline_response2011 import InlineResponse2011  # noqa: E501
from swagger_server import util
from ..utils.auth_utils import authenticate_token, require_admin
from datetime import datetime
from ..database.database import get_all_books_from_db, delete_book_by_id, update_book_by_id, insert_new_book
books = get_all_books_from_db()
from flask import jsonify

@authenticate_token
def create_book(body):  # noqa: E501
    """Thêm sách mới

    Tạo một sách mới trong hệ thống (yêu cầu xác thực) # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse2011
    """
    global books
    if not connexion.request.is_json:
        return (
            {
                "success": False,
                "message": "Request body phải là JSON",
            },
            400,
        )
    data = BookInput.from_dict(connexion.request.get_json())  # noqa: E501
    title = data.title
    author = data.author
    year = data.year or datetime.now().year
    price = data.price or 0.0
    # Validation
    if not title or not author:
        return {"success": False, "message": "Title và Author là bắt buộc"}, 400
        

    new_book = {
        "title": title,
        "author": author,
        "year": year,
        "price": price,
    }
    insert_new_book(title=title, author=author, year=year, price=price)
    books.append(new_book)
    books = get_all_books_from_db()
    return {"success": True, "data": new_book}, 201

@authenticate_token
@require_admin
def delete_book(id_):  # noqa: E501
    """Xóa sách

    Xóa một sách khỏi hệ thống (yêu cầu xác thực) # noqa: E501

    :param id: ID của sách
    :type id: int

    :rtype: InlineResponse2004
    """
    global books
    book = next((b for b in books if b["id"] == id_), None)

    if not book:
        return {"success": False, "message": "Không tìm thấy sách"}, 404

    books = [b for b in books if b["id"] != id_]
    delete_book_by_id(id_)
    books = get_all_books_from_db()
    return {"success": True, "message": "Xóa sách thành công"}


def get_all_books():  # noqa: E501
    """Lấy danh sách tất cả sách

    Trả về danh sách tất cả sách trong hệ thống # noqa: E501


    :rtype: InlineResponse2003
    """
    return {"success": True, "data": books}


def get_book_by_id(id_):  # noqa: E501
    """Lấy thông tin sách theo ID

    Trả về thông tin chi tiết của một sách # noqa: E501

    :param id: ID của sách
    :type id: int

    :rtype: InlineResponse2011
    """
    book = next((b for b in books if b["id"] == id_), None)

    if not book:
        return {"success": False, "message": "Không tìm thấy sách"}, 404

    return {"success": True, "data": book}

@authenticate_token
def update_book(body, id_):  # noqa: E501
    """Cập nhật thông tin sách

    Cập nhật toàn bộ thông tin của một sách (yêu cầu xác thực) # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param id: ID của sách
    :type id: int

    :rtype: InlineResponse2011
    """
    if not connexion.request.is_json:
        return (
            {
                "success": False,
                "message": "Request body phải là JSON",
            },
            400,
        )
    
    data = BookInput.from_dict(connexion.request.get_json())  # noqa: E501
    book = next((b for b in books if b["id"] == id_), None)

    if not book:
        return {"success": False, "message": "Không tìm thấy sách"}, 404


    title = data.title
    author = data.author

    if not title or not author:
        return (
            {"success": False, "message": "Title và Author là bắt buộc"},
            400,
        )

    book["title"] = title
    book["author"] = author
    book["year"] = data.year or book["year"]
    book["price"] = data.price or book["price"]
    book_copy = book.copy()
    book_copy.pop("id", None)
    book_copy.pop("_id", None)
    update_book_by_id(id_, book_copy)
    return {"success": True, "data": book}
