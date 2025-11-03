# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.book_input import BookInput  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response2003 import InlineResponse2003  # noqa: E501
from swagger_server.models.inline_response2004 import InlineResponse2004  # noqa: E501
from swagger_server.models.inline_response2011 import InlineResponse2011  # noqa: E501
from swagger_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_create_book(self):
        """Test case for create_book

        Thêm sách mới
        """
        body = BookInput()
        response = self.client.open(
            '/api/books',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_book(self):
        """Test case for delete_book

        Xóa sách
        """
        response = self.client.open(
            '/api/books/{id}'.format(id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_books(self):
        """Test case for get_all_books

        Lấy danh sách tất cả sách
        """
        response = self.client.open(
            '/api/books',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_book_by_id(self):
        """Test case for get_book_by_id

        Lấy thông tin sách theo ID
        """
        response = self.client.open(
            '/api/books/{id}'.format(id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_book(self):
        """Test case for update_book

        Cập nhật thông tin sách
        """
        body = BookInput()
        response = self.client.open(
            '/api/books/{id}'.format(id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
