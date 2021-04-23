import sqlite3
from sqlite3 import Error
class SQL_Manager:
    def __init__(self):
        self.connection = None
        try:
            self.connection = sqlite3.connect("data.sqlite")
        except Error as e:
            print(f"Error {e} ")

    def __execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print(f"Error {e}")

if __name__ == "__main__":
    DB = SQL_Manager()
