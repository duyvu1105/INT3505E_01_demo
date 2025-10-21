from flask import Flask, jsonify

app = Flask(__name__)
port = 3001 # Chạy ở cổng khác

# --- Mock Database (đã chuẩn hóa key) ---
mock_users = [
  { "id": 1, "name": "Alice" },
  { "id": 2, "name": "Bob" }
]

mock_products = [
  { "id": 101, "name": "Laptop" }, # <-- 'id' thay vì 'product_id'
  { "id": 102, "name": "Mouse" }  # <-- 'name' thay vì 'productName'
]
# ---------------------

# Một "quy tắc" (helper function) để tạo response nhất quán
def create_api_success_response(data_list):
    return {
        "data": data_list,
        "pagination": {
            "totalItems": len(data_list)
        }
    }

# API 1: /users
@app.route('/users', methods=['GET'])
def get_users_consistent():
    print('Got request for /users')
    # Luôn dùng chung một cấu trúc
    return jsonify(create_api_success_response(mock_users))

# API 2: /products
@app.route('/products', methods=['GET'])
def get_products_consistent():
    print('Got request for /products')
    # Luôn dùng chung một cấu trúc
    return jsonify(create_api_success_response(mock_products))

if __name__ == '__main__':
    print(f" API NHẤT QUÁN đang chạy tại http://localhost:{port}")
    app.run(port=port)