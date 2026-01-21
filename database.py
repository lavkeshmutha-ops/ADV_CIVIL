
import mysql.connector
from mysql.connector import Error

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            try:
                cls._instance.connection = mysql.connector.connect(
                    host='localhost',
                    user='root',       # Update with local MySQL credentials
                    password='password',
                    database='lex_guardian'
                )
            except Error as e:
                print(f"Error connecting to MySQL: {e}")
                cls._instance.connection = None
        return cls._instance

    def get_cursor(self):
        if self.connection and self.connection.is_connected():
            return self.connection.cursor(dictionary=True)
        return None

    def commit(self):
        if self.connection:
            self.connection.commit()

db = Database()
