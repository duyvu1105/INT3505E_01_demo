from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

app = Flask(__name__)

# DB GIẢ LẬP
books: Dict[int, Dict[str, Any]] = {}
users: Dict[int, Dict[str, Any]] = {}
loans: Dict[int, Dict[str, Any]] = {}

seq = {"book": 0, "user": 0, "loan": 0}

def next_id(kind: str) -> int:
    seq[kind] += 1
    return seq[kind]

def iso_now() -> str:
    return datetime.utcnow().isoformat() + "Z"

# Dữ liệu mẫu
def seed_data():
    if not books and not users and not loans:
        b1 = next_id("book")
        books[b1] = {
            "id": b1,
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "total_copies": 3,
            "available": 3,
        }
        b2 = next_id("book")
        books[b2] = {
            "id": b2,
            "title": "Design Patterns",
            "author": "Gamma et al.",
            "total_copies": 2,
            "available": 2,
        }

        u1 = next_id("user")
        users[u1] = {"id": u1, "name": "Alice"}
        u2 = next_id("user")
        users[u2] = {"id": u2, "name": "Bob"}

seed_data()

# Helpers
def get_json() -> Dict[str, Any]:
    if not request.is_json:
        return {}
    return request.get_json(silent=True) or {}

def err(msg: str, code: int = 400):
    return jsonify({"error": msg}), code

def find_book(book_id: int) -> Optional[Dict[str, Any]]:
    return books.get(book_id)

def find_user(user_id: int) -> Optional[Dict[str, Any]]:
    return users.get(user_id)

def active_loans_for_book(book_id: int) -> int:
    return sum(1 for l in loans.values() if l["book_id"] == book_id and l["returned_at"] is None)

# Health
@app.get("/health")
def health():
    return jsonify({"status": "ok", "time": iso_now()})

# Books
@app.get("/books")
def list_books():
    return jsonify(list(books.values()))

@app.post("/books")
def create_book():
    data = get_json()
    title = data.get("title")
    author = data.get("author")
    total = data.get("total_copies", 1)

    if not title or not author:
        return err("title và author là bắt buộc")
    if not isinstance(total, int) or total < 1:
        return err("total_copies phải là số nguyên >= 1")

    book_id = next_id("book")
    books[book_id] = {
        "id": book_id,
        "title": title,
        "author": author,
        "total_copies": total,
        "available": total,
    }
    return jsonify(books[book_id]), 201

@app.get("/books/<int:book_id>")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return err("Không tìm thấy sách", 404)
    return jsonify(book)

@app.put("/books/<int:book_id>")
def update_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return err("Không tìm thấy sách", 404)
    data = get_json()

    # Cho phép cập nhật title/author/total_copies
    if "title" in data:
        book["title"] = data["title"]
    if "author" in data:
        book["author"] = data["author"]
    if "total_copies" in data:
        new_total = data["total_copies"]
        if not isinstance(new_total, int) or new_total < 1:
            return err("total_copies phải là số nguyên >= 1")
        # Đảm bảo available không vượt quá total và không âm
        active = active_loans_for_book(book_id)
        if new_total < active:
            return err(f"total_copies < số lượt mượn đang active ({active})")
        # Điều chỉnh available dựa trên active
        book["total_copies"] = new_total
        book["available"] = new_total - active

    return jsonify(book)

@app.delete("/books/<int:book_id>")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return err("Không tìm thấy sách", 404)
    # Chỉ cho xóa khi không có loan đang active
    if active_loans_for_book(book_id) > 0:
        return err("Không thể xóa: sách đang có lượt mượn chưa trả")
    del books[book_id]
    return "", 204

# Users
@app.get("/users")
def list_users():
    return jsonify(list(users.values()))

@app.post("/users")
def create_user():
    data = get_json()
    name = data.get("name")
    if not name:
        return err("name là bắt buộc")
    user_id = next_id("user")
    users[user_id] = {"id": user_id, "name": name}
    return jsonify(users[user_id]), 201

# Loans: Borrow / Return
@app.get("/loans")
def list_loans():
    active = request.args.get("active")
    items = list(loans.values())
    if active is not None:
        want_active = active.lower() in ("1", "true", "yes")
        items = [l for l in items if (l["returned_at"] is None) == want_active]
    return jsonify(items)

@app.post("/borrow")
def borrow():
    data = get_json()
    book_id = data.get("book_id")
    user_id = data.get("user_id")
    days = data.get("days", 14)

    if not isinstance(book_id, int) or not isinstance(user_id, int):
        return err("book_id và user_id phải là số nguyên")
    book = find_book(book_id)
    if not book:
        return err("Không tìm thấy sách", 404)
    user = find_user(user_id)
    if not user:
        return err("Không tìm thấy user", 404)
    if book["available"] < 1:
        return err("Sách hết bản để mượn")

    loan_id = next_id("loan")
    borrowed_at = datetime.utcnow()
    due_at = borrowed_at + timedelta(days=int(days))
    loans[loan_id] = {
        "id": loan_id,
        "book_id": book_id,
        "user_id": user_id,
        "borrowed_at": borrowed_at.isoformat() + "Z",
        "due_at": due_at.isoformat() + "Z",
        "returned_at": None,
    }
    book["available"] -= 1
    return jsonify(loans[loan_id]), 201

@app.post("/return")
def return_book():
    data = get_json()
    loan_id = data.get("loan_id")
    if not isinstance(loan_id, int):
        return err("loan_id phải là số nguyên")
    loan = loans.get(loan_id)
    if not loan:
        return err("Không tìm thấy loan", 404)
    if loan["returned_at"] is not None:
        return err("Loan đã được trả trước đó")

    loan["returned_at"] = iso_now()
    # Tăng available cho sách
    book = find_book(loan["book_id"])
    if book:
        # đảm bảo không vượt quá total_copies
        if book["available"] < book["total_copies"]:
            book["available"] += 1
    return jsonify(loan)

# Chạy app
if __name__ == "__main__":
    app.run(debug=True)
