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

    def test_get_current_user(self):
        """Test case for get_current_user

        Lấy thông tin người dùng hiện tại
        """
        response = self.client.open(
            '/api/auth/me',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_login(self):
        """Test case for login

        Đăng nhập
        """
        body = AuthLoginBody()
        response = self.client.open(
            '/api/auth/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_refresh_token(self):
        """Test case for refresh_token

        Cấp lại access token từ refresh token
        """
        body = AuthRefreshBody()
        response = self.client.open(
            '/api/auth/refresh',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_register(self):
        """Test case for register

        Đăng ký tài khoản mới
        """
        body = AuthRegisterBody()
        response = self.client.open(
            '/api/auth/register',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
