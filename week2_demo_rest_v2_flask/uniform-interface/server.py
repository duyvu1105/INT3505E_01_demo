from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data
items = [
    {'id': 1, 'name': 'Item 1'},
    {'id': 2, 'name': 'Item 2'},
]

# 1. Tài nguyên được xác định bằng URL
# 2. Thao tác qua biểu diễn (server trả về JSON)
# 3. Thông điệp tự mô tả (Mỗi message chứa đủ thông tin)
# 4. Phản hồi bao gồm các liên kết (HATEOAS)

@app.route('/items', methods=['GET'])
def get_items():
    """Get all items with HATEOAS links"""
    response = {
        'data': items,
        '_links': {
            'self': {'href': '/items'},
            'find': {'href': '/items/{id}', 'method': 'GET'}
        }
    }
    return jsonify(response)


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get single item with HATEOAS links"""
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # HATEOAS: Thêm links để client biết các hành động có thể thực hiện
    response = {
        **item,
        '_links': {
            'self': {'href': f'/items/{item["id"]}'},           # Link đến chính nó
            'update': {'href': f'/items/{item["id"]}', 'method': 'PUT'},    # Link để update
            'delete': {'href': f'/items/{item["id"]}', 'method': 'DELETE'}, # Link để delete
            'collection': {'href': '/items'}                 # Link về collection
        }
    }
    
    return jsonify(response)


@app.route('/items', methods=['POST'])
def create_item():
    """Create new item"""
    data = request.get_json()
    new_item = {
        'id': len(items) + 1,
        'name': data.get('name')
    }
    items.append(new_item)
    return jsonify(new_item), 201


@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update item"""
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    item['name'] = data.get('name')
    return jsonify(item)


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete item"""
    global items
    item_index = next((i for i, item in enumerate(items) if item['id'] == item_id), None)
    if item_index is None:
        return jsonify({'error': 'Item not found'}), 404
    
    items.pop(item_index)
    return '', 204


if __name__ == '__main__':
    print('Server is running on http://localhost:5000')
    app.run(debug=True, port=5000)
