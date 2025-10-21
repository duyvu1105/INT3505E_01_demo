from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 1. Tên Endpoint dùng danh từ (resource)
# RÕ RÀNG: 'POST' lên '/users' có nghĩa là "tạo một user mới".
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    # Thông báo lỗi rõ ràng, cụ thể
    if not user_data.get('email'):
        # RÕ RÀNG: Client biết ngay lỗi ở trường 'email' và lý do là 'required'.
        return jsonify({
            "error": {
                "code": "VALIDATION_FAILED",
                "field": "email",
                "message": "Email field is required and cannot be empty."
            }
        }), 400

    # 2. Tên trường (key) trong response tự mô tả
    # RÕ RÀNG: 'name' và 'createdAt' rất dễ hiểu.
    # Dùng chuẩn ISO 8601 cho ngày tháng.
    return jsonify({
        "id": 1,
        "name": user_data.get('name'), 
        "createdAt": datetime.now().isoformat() 
    }), 201

# 3. Tên tham số (parameter) đầy đủ ý nghĩa
# RÕ RÀNG: Client biết chính xác 'status' và 'page' dùng để làm gì.
@app.route('/articles', methods=['GET'])
def get_articles_clear():
    status = request.args.get('status') # 'status' thay vì 's'
    page = request.args.get('page', default=1, type=int) # 'page' thay vì 'p'
    
    return jsonify({
        "filters": {
            "status": status,
            "page": page
        },
        "data": [{"id": 1, "title": "Article 1"}] # (Thường dùng 'data' cho nhất quán)
    })

if __name__ == '__main__':
    app.run(port=5001) 