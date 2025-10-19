from datetime import datetime, timedelta
import re
import json


class Book:
    """Book Model - Validation và helper methods"""
    
    @staticmethod
    def validate(data):
        """
        Validate book data
        Returns: (is_valid: bool, errors: list)
        """
        errors = []
        
        if not data.get('title') or not data['title'].strip():
            errors.append('Title là bắt buộc')
        
        if not data.get('author') or not data['author'].strip():
            errors.append('Author là bắt buộc')
        
        if not data.get('isbn') or not data['isbn'].strip():
            errors.append('ISBN là bắt buộc')
        
        # Validate ISBN format
        if data.get('isbn') and not re.match(r'^[0-9-]+$', data['isbn']):
            errors.append('ISBN chỉ chứa số và dấu gạch ngang')
        
        # Validate year
        if 'published_year' in data and data['published_year']:
            try:
                year = int(data['published_year'])
                if year < 1000 or year > datetime.now().year:
                    errors.append(f'Năm xuất bản không hợp lệ')
            except:
                errors.append('Năm xuất bản phải là số')
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def create(data):
        """Tạo book dict với default values"""
        return {
            'title': data['title'],
            'author': data['author'],
            'isbn': data['isbn'],
            'published_year': data.get('published_year'),
            'category': data.get('category', 'Uncategorized'),
            'quantity': data.get('quantity', 1),
            'available': data.get('quantity', 1)
        }
    
    @staticmethod
    def is_available(book):
        """Kiểm tra sách có sẵn để mượn không"""
        return book.get('available', 0) > 0
    
    @staticmethod
    def has_borrowed_books(book):
        """Kiểm tra sách có đang được mượn không"""
        return book.get('available', 0) < book.get('quantity', 0)
    
    @staticmethod
    def get_borrowed_count(book):
        """Số sách đang được mượn"""
        return book.get('quantity', 0) - book.get('available', 0)


class User:
    """User Model - Validation và helper methods"""
    
    @staticmethod
    def validate(data):
        """
        Validate user data
        Returns: (is_valid: bool, errors: list)
        """
        errors = []
        
        if not data.get('name') or not data['name'].strip():
            errors.append('Name là bắt buộc')
        
        if not data.get('email') or not data['email'].strip():
            errors.append('Email là bắt buộc')
        
        if not data.get('phone') or not data['phone'].strip():
            errors.append('Phone là bắt buộc')
        
        # Validate email
        if data.get('email') and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', data['email']):
            errors.append('Email không hợp lệ')
        
        # Validate phone
        phone = data.get('phone', '').replace(' ', '').replace('-', '')
        if phone and not re.match(r'^[0-9]{10,11}$', phone):
            errors.append('Phone phải có 10-11 chữ số')
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def create(data):
        """Tạo user dict với default values"""
        return {
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data.get('address', ''),
            'status': data.get('status', 'active'),
            'borrowed_books': '[]'
        }
    
    @staticmethod
    def can_borrow(user):
        """Kiểm tra user có thể mượn sách không"""
        borrowed = json.loads(user.get('borrowed_books', '[]'))
        return user.get('status') == 'active' and len(borrowed) < 5
    
    @staticmethod
    def is_active(user):
        """Kiểm tra user đang active không"""
        return user.get('status') == 'active'
    
    @staticmethod
    def has_borrowed_books(user):
        """Kiểm tra user có sách đang mượn không"""
        borrowed = json.loads(user.get('borrowed_books', '[]'))
        return len(borrowed) > 0


class Borrowing:
    """Borrowing Model - Validation và helper methods"""
    
    @staticmethod
    def validate(data):
        """
        Validate borrowing data
        Returns: (is_valid: bool, errors: list)
        """
        errors = []
        
        if not data.get('user_id'):
            errors.append('User ID là bắt buộc')
        
        if not data.get('book_id'):
            errors.append('Book ID là bắt buộc')
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def create(data):
        """Tạo borrowing dict với default values"""
        borrow_date = data.get('borrow_date', datetime.now().strftime('%Y-%m-%d'))
        due_date = data.get('due_date', Borrowing.calculate_due_date(borrow_date))
        
        return {
            'user_id': int(data['user_id']),
            'book_id': int(data['book_id']),
            'borrow_date': borrow_date,
            'due_date': due_date,
            'status': 'borrowed',
            'fine': 0
        }
    
    @staticmethod
    def calculate_due_date(borrow_date=None):
        """Tính ngày hạn trả (14 ngày sau ngày mượn)"""
        if borrow_date:
            borrow = datetime.strptime(borrow_date, '%Y-%m-%d')
        else:
            borrow = datetime.now()
        
        due = borrow + timedelta(days=14)
        return due.strftime('%Y-%m-%d')
    
    @staticmethod
    def is_overdue(borrowing):
        """Kiểm tra có quá hạn không"""
        if borrowing.get('status') == 'returned':
            return False
        
        today = datetime.now().strftime('%Y-%m-%d')
        return borrowing.get('due_date', '') < today
    
    @staticmethod
    def calculate_fine(borrowing, return_date=None):
        """Tính phí phạt (1000 VNĐ/ngày)"""
        actual_return = return_date or datetime.now().strftime('%Y-%m-%d')
        
        due_date = datetime.strptime(borrowing['due_date'], '%Y-%m-%d')
        return_d = datetime.strptime(actual_return, '%Y-%m-%d')
        
        if return_d <= due_date:
            return 0
        
        days_overdue = (return_d - due_date).days
        return days_overdue * 1000
    
    @staticmethod
    def update_overdue_status(borrowing):
        """Cập nhật status thành overdue và tính fine"""
        if Borrowing.is_overdue(borrowing) and borrowing.get('status') == 'borrowed':
            borrowing['status'] = 'overdue'
            borrowing['fine'] = Borrowing.calculate_fine(borrowing)
        
        return borrowing
