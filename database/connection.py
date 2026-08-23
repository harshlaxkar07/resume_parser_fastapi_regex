import pymysql
from pymysql.cursors import DictCursor


# =====================================================
# Database Configuration
# =====================================================

HOST = "localhost"
PORT = 3306
USER = "root_user"
PASSWORD = "password"
DATABASE = "pdf_parser"


# =====================================================
# Create Database Connection
# =====================================================

def get_connection():
    """
    Creates and returns a new MySQL database connection.
    """

    connection = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        cursorclass=DictCursor,
        autocommit=True
    )

    return connection