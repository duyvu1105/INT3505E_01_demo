# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="Books Management API",
    author_email="support@example.com",
    url="",
    keywords=["Swagger", "Books Management API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    API quản lý sách với xác thực JWT.  **Tài khoản demo:** - Username: &#x60;admin&#x60; / Password: &#x60;admin123&#x60; (role: admin) - Username: &#x60;user&#x60; / Password: &#x60;user123&#x60; (role: user) 
    """
)
