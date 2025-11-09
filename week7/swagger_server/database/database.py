
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import json
from bson.objectid import ObjectId # Để xử lý ObjectId
from bson.json_util import dumps, loads # Để xử lý JSON hóa ObjectId
from dotenv import load_dotenv
import certifi

load_dotenv()

mongodb_username = os.getenv('MONGODB_USERNAME')
mongodb_password = os.getenv('MONGODB_PASSWORD')
uri = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.4auoddj.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tls=True, tlsCAFile=certifi.where())

# Dữ liệu mẫu của bạn
books_data = [
    {"title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "price": 45.99},
    {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "year": 1999, "price": 42.5},
    {"title": "Design Patterns", "author": "Gang of Four", "year": 1994, "price": 54.99},
]

users_data = [
    {"username": "admin", "password": "admin123", "email": "admin@example.com", "role": "admin"},
    {"username": "user", "password": "user123", "email": "user@example.com", "role": "user"},
]

def test_connection():
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

def create_database():
    # Gọi hàm kiểm tra kết nối
    test_connection()
    db = client.book_db
    db.refresh_tokens.create_index("expireAt", expireAfterSeconds=0)

    # Lấy collections (tương đương "bảng")
    refresh_tokens_collection = db.refresh_tokens
    books_collection = db.books
    users_collection = db.users

    # Xóa dữ liệu cũ (nếu có) để tránh trùng lặp khi chạy lại script
    books_collection.delete_many({})
    users_collection.delete_many({})
    refresh_tokens_collection.delete_many({})

    # Chèn dữ liệu mới
    books_collection.insert_many(books_data)
    users_collection.insert_many(users_data)

    print("Đã chèn dữ liệu mẫu thành công!")
    print(f"Tổng số sách: {books_collection.count_documents({})}")
    print(f"Tổng số user: {users_collection.count_documents({})}")

def mongo_to_json(data):
    # dumps sẽ chuyển ObjectId thành chuỗi
    # loads sẽ biến chuỗi JSON đó trở lại thành đối tượng Python (dict/list)
    return json.loads(dumps(data))

def get_all_users():
    db = client.book_db
    users_collection = db.users

    users = list(users_collection.find())  # Lấy tất cả tài liệu
    for user in users:
        user['id'] = str(user['_id'])
    return mongo_to_json(users)


def get_all_books_from_db():
    db = client.book_db
    books_collection = db.books

    books = list(books_collection.find())  # Lấy tất cả tài liệu
    for book in books:
        book['id'] = str(book['_id'])
    return mongo_to_json(books)

def save_refresh_token(user_id, token, expire_at):
    db = client.book_db
    refresh_tokens_collection = db.refresh_tokens

    refresh_token_doc = {
        "user_id": user_id,
        "token": token,
        "expireAt": expire_at  # Trường này sẽ được MongoDB sử dụng để tự động xóa tài liệu khi hết hạn
    }
    refresh_tokens_collection.insert_one(refresh_token_doc)

def get_refresh_token(user_id, refresh_token):
    db = client.book_db
    refresh_tokens_collection = db.refresh_tokens

    refresh_token_doc = refresh_tokens_collection.find_one({
        "user_id": user_id,
        "token": refresh_token
    })

    return refresh_token_doc

def insert_new_user(username, password, email, role):
    db = client.book_db
    users_collection = db.users

    new_user = {
        "username": username,
        "password": password,
        "email": email,
        "role": role
    }
    result = users_collection.insert_one(new_user)
    return str(result.inserted_id)

def insert_new_book(title, author, year, price):
    db = client.book_db
    books_collection = db.books

    new_book = {
        "title": title,
        "author": author,
        "year": year,
        "price": price
    }
    result = books_collection.insert_one(new_book)
    return str(result.inserted_id)

def delete_book_by_id(book_id):
    db = client.book_db
    books_collection = db.books

    result = books_collection.delete_one({"_id": ObjectId(book_id)})
    return result.deleted_count

def update_book_by_id(book_id, updated_data):
    db = client.book_db
    books_collection = db.books

    result = books_collection.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": updated_data}
    )
    return result.modified_count