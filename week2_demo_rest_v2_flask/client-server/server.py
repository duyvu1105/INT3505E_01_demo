from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data
items = [
    {'id': 1, 'name': 'Item 1'},
    {'id': 2, 'name': 'Item 2'},
]

@app.route('/items', methods=['GET'])
def get_items():
    """Get all items"""
    return jsonify(items)


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get single item"""
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return {'error': 'Item not found'}, 404
    
    return jsonify(item)


if __name__ == '__main__':
    print('Server is running on http://localhost:5000')
    app.run(debug=True, port=5000)
