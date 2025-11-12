"""
Locust Load Testing cho Books API
Tương tự như Newman test nhưng dùng Python và có thể test hiệu năng
"""

from locust import HttpUser, task, between, SequentialTaskSet
import json


class AuthenticatedUser(SequentialTaskSet):
    """Test suite với authentication flow"""
    
    access_token = None
    refresh_token = None
    book_id = None
    
    def on_start(self):
        """Chạy trước khi bắt đầu test - giống như Pre-request Script trong Postman"""
        print("Starting test suite...")
    
    @task
    def test_1_register_user(self):
        """Test 1: Đăng ký tài khoản mới"""
        response = self.client.post(
            "/api/auth/register",
            json={
                "username": f"testuser_{self.user.client_id}",
                "password": "testpass123",
                "email": f"testuser_{self.user.client_id}@example.com"
            },
            name="POST /api/auth/register"
        )
        
        if response.status_code in [201, 400]:  # 201 = created, 400 = already exists
            print(f"✓ Register: {response.status_code}")
        else:
            print(f"✗ Register failed: {response.status_code}")
    
    @task
    def test_2_login(self):
        """Test 2: Đăng nhập - Lưu token giống Newman environment variables"""
        response = self.client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            },
            name="POST /api/auth/login"
        )
        
        if response.status_code == 200:
            data = response.json()
            # Lưu token giống như set environment variable trong Postman/Newman
            self.access_token = data['data']['access_token']
            self.refresh_token = data['data']['refresh_token']
            print(f"✓ Login successful - Token saved")
        else:
            print(f"✗ Login failed: {response.status_code}")
    
    @task
    def test_3_get_current_user(self):
        """Test 3: Lấy thông tin user hiện tại - Sử dụng Bearer token"""
        if not self.access_token:
            print("✗ No access token - skipping test")
            return
        
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="GET /api/auth/me"
        )
        
        if response.status_code == 200:
            print(f"✓ Get current user: {response.json()['data']['username']}")
        else:
            print(f"✗ Get current user failed: {response.status_code}")
    
    @task
    def test_4_refresh_token(self):
        """Test 4: Refresh token"""
        if not self.refresh_token:
            print("✗ No refresh token - skipping test")
            return
        
        response = self.client.post(
            "/api/auth/refresh",
            json={"refresh_token": self.refresh_token},
            name="POST /api/auth/refresh"
        )
        
        if response.status_code == 200:
            data = response.json()
            # Update access token
            self.access_token = data['access_token']
            print(f"✓ Token refreshed successfully")
        else:
            print(f"✗ Refresh token failed: {response.status_code}")
    
    @task
    def test_5_get_all_books(self):
        """Test 5: Lấy danh sách tất cả sách"""
        response = self.client.get(
            "/api/books",
            name="GET /api/books"
        )
        
        if response.status_code == 200:
            data = response.json()
            books_count = len(data['data'])
            print(f"✓ Get all books: {books_count} books found")
            
            # Lưu book_id đầu tiên để dùng cho test sau
            if books_count > 0:
                self.book_id = data['data'][0]['id']
        else:
            print(f"✗ Get all books failed: {response.status_code}")
    
    @task
    def test_6_get_book_by_id(self):
        """Test 6: Lấy thông tin sách theo ID"""
        if not self.book_id:
            print("✗ No book ID - skipping test")
            return
        
        response = self.client.get(
            f"/api/books/{self.book_id}",
            name="GET /api/books/{id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Get book by ID: {data['data']['title']}")
        else:
            print(f"✗ Get book by ID failed: {response.status_code}")
    
    @task
    def test_7_create_book(self):
        """Test 7: Tạo sách mới - Cần authentication"""
        if not self.access_token:
            print("✗ No access token - skipping test")
            return
        
        response = self.client.post(
            "/api/books",
            json={
                "title": f"Locust Test Book {self.user.client_id}",
                "author": "Locust Tester",
                "year": 2024,
                "price": 29.99
            },
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="POST /api/books"
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Book created: {data['data']['title']}")
        else:
            print(f"✗ Create book failed: {response.status_code}")
    
    @task
    def test_8_update_book(self):
        """Test 8: Cập nhật thông tin sách - Cần authentication"""
        if not self.access_token or not self.book_id:
            print("✗ Missing token or book ID - skipping test")
            return
        
        response = self.client.put(
            f"/api/books/{self.book_id}",
            json={
                "title": "Updated Book Title",
                "author": "Updated Author",
                "year": 2025,
                "price": 39.99
            },
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="PUT /api/books/{id}"
        )
        
        if response.status_code == 200:
            print(f"✓ Book updated successfully")
        else:
            print(f"✗ Update book failed: {response.status_code}")
    
    @task
    def test_9_delete_book(self):
        """Test 9: Xóa sách - Cần admin token"""
        if not self.access_token or not self.book_id:
            print("✗ Missing token or book ID - skipping test")
            return
        
        # Login as admin để có quyền xóa
        admin_login = self.client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if admin_login.status_code == 200:
            admin_token = admin_login.json()['data']['access_token']
            
            response = self.client.delete(
                f"/api/books/{self.book_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                name="DELETE /api/books/{id}"
            )
            
            if response.status_code == 200:
                print(f"✓ Book deleted successfully")
            else:
                print(f"✗ Delete book failed: {response.status_code}")


class APIUser(HttpUser):
    """
    Định nghĩa user ảo để test API
    - wait_time: Thời gian chờ giữa các request (giống như iteration delay trong Postman)
    - host: Base URL của API
    """
    tasks = [AuthenticatedUser]
    wait_time = between(1, 3)  # Chờ 1-3 giây giữa các task
    
    # Tạo client_id unique cho mỗi user
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = id(self)


# Class riêng cho functional testing (không loop)
class FunctionalTestUser(HttpUser):
    """User cho functional testing - chạy 1 lần như Newman"""
    tasks = [AuthenticatedUser]
    wait_time = between(0.5, 1)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = id(self)


if __name__ == "__main__":
    print("Run with: locust -f locustfile.py --host=http://localhost:5000")
