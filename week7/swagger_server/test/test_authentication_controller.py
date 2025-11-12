# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.auth_login_body import AuthLoginBody  # noqa: E501
from swagger_server.models.auth_refresh_body import AuthRefreshBody  # noqa: E501
from swagger_server.models.auth_register_body import AuthRegisterBody  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from swagger_server.models.inline_response201 import InlineResponse201  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAuthenticationController(BaseTestCase):
    """AuthenticationController integration test stubs"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        self.access_token = None
        self.refresh_token = None

    def test_register(self):
        """Test case for register

        Đăng ký tài khoản mới
        """
        body = {
            "username": "testuser",
            "password": "testpass123",
            "email": "testuser@example.com"
        }
        response = self.client.open(
            '/api/auth/register',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        
        # Kiểm tra status code là 201 (Created) hoặc 400 nếu user đã tồn tại
        self.assertIn(response.status_code, [201, 400],
                      'Response body is : ' + response.data.decode('utf-8'))

    def test_login(self):
        """Test case for login

        Đăng nhập
        """
        body = {
            "username": "admin",
            "password": "admin123"
        }
        response = self.client.open(
            '/api/auth/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        
        # Lưu token để dùng cho các test khác
        data = json.loads(response.data.decode('utf-8'))
        if 'data' in data and 'access_token' in data['data']:
            self.access_token = data['data']['access_token']
            self.refresh_token = data['data']['refresh_token']

    def test_get_current_user(self):
        """Test case for get_current_user

        Lấy thông tin người dùng hiện tại
        """
        # Đăng nhập trước để lấy token
        login_body = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = self.client.open(
            '/api/auth/login',
            method='POST',
            data=json.dumps(login_body),
            content_type='application/json')
        
        login_data = json.loads(login_response.data.decode('utf-8'))
        token = login_data['data']['access_token']
        
        # Gọi API với token
        response = self.client.open(
            '/api/auth/me',
            method='GET',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_refresh_token(self):
        """Test case for refresh_token

        Cấp lại access token từ refresh token
        """
        # Đăng nhập trước để lấy refresh token
        login_body = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = self.client.open(
            '/api/auth/login',
            method='POST',
            data=json.dumps(login_body),
            content_type='application/json')
        
        login_data = json.loads(login_response.data.decode('utf-8'))
        refresh_token = login_data['data']['refresh_token']
        
        # Test refresh token
        body = {
            "refresh_token": refresh_token
        }
        response = self.client.open(
            '/api/auth/refresh',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
