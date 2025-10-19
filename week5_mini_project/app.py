from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db
from routes import book_bp, user_bp, borrowing_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints (Routes)
app.register_blueprint(book_bp, url_prefix='/api/books')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(borrowing_bp, url_prefix='/api/borrowings')

# ==================== ROOT ROUTE ====================

@app.route('/')
def index():
    return jsonify({
        'message': 'Library Management System API',
        'version': '2.0.0 (Flask + SQLite3 + Models + Routes)',
        'endpoints': {
            'books': '/api/books',
            'users': '/api/users',
            'borrowings': '/api/borrowings'
        }
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint không tồn tại'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Lỗi server'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    init_db()
    
    PORT = 3000
    print('\n' + '='*60)
    print('Library Management System API (Flask + SQLite3)')
    print('='*60)
    print('Endpoints:')
    print(f'Books:      http://localhost:{PORT}/api/books')
    print(f'Users:      http://localhost:{PORT}/api/users')
    print(f'Borrowings: http://localhost:{PORT}/api/borrowings')
    print('='*60 + '\n')
    
    app.run(debug=True, host='0.0.0.0', port=PORT)
