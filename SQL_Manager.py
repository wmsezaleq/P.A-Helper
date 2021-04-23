import sqlite3
from sqlite3 import Error

class SQL_Manager:
    def __init__(self, DB_name):
        self.DB_name = DB_name
        self.__connection = None
        try:
            self.__connection = sqlite3.connect(f"{DB_name}.sqlite3")
            self.__cursor = self.__connection.cursor()
        except Error as e:
            print(f"Error creando la database: {e}")

    def execute(self, query):
        self.__cursor.execute(query + ";")
        self.__connection.commit()

    def __fetch(self):
        return self.__cursor.fetchall()


    def create_table(self, table_name, *values):
        try:
            values_str = ""
            for index, item in enumerate(values):
                values_str += f"'{item[0]}' {item[1]}"
                if index != len(values)-1:
                    values_str +=", "
            self.execute(f"""
                            CREATE TABLE
                                IF NOT EXISTS '{table_name}'
                                ({values_str})
                            """)
        except Exception as e:
            print(f"Error creando tabla {table_name}: {e}")
    def delete_from_table(self, table_name, condition):
        try:
            where = ""
            if condition:
                where = f"WHERE {condition}"
            self.execute(f"""
                            DELETE FROM '{table_name}' {where}
                            """)
        except Exception as e:
            print(f"Error eliminando valor de {table_name}: {e}")
    def delete_table(self, table_name):
        self.execute(f"DROP TABLE '{table_name}'")
    def insert(self, table_name, *values):
        try:
            values_str = ""
            for index, value in enumerate(values):
                values_str += "("
                if len(value) > 1:
                    for i, item in enumerate(value):
                        if type(item) == str:
                            values_str += f"'{item}'"
                        else:
                            values_str += str(item)
                        if i != len(value)-1:
                            values_str += ', '
                    values_str += ")"
                    if index != len(values)-1:
                        values_str += ", "
                else:
                    if type(value) == tuple:
                        if type(value[0]) == str:
                            values_str += f"'{value[0]}'"
                        else:
                            values_str += value[0]
                    values_str += ")"
            self.execute(f"INSERT INTO '{table_name}' VALUES{values_str}")
        except Exception as e:
            print(f"Error insertando informacion en {table_name}: {e}")
    def get(self, table_name, column, *condicion):
        try:
            where = ""
            if condicion:
                where = f"WHERE {condicion[0]}"
            self.__cursor.execute(f"SELECT {column} FROM {table_name} {where}")
            return self.__fetch()
        except Exception as e:
            print(f"Error obteniendo informacion de {table_name}: {e}")


    def update(self, table_name, values, *condicion):
        try:
            where = ""
            if condicion:
                where = f"WHERE {condicion[0]}"
            self.execute(f"UPDATE {table_name} SET {values} {where}")
        except Exception as e:
            print(f"Error actualizando informacion en {table_name}: {e}")
    
    def __del__(self):
        self.__cursor.close()
        self.__connection.close()

if __name__ == "__main__":
    Database = SQL_Manager(DB_name="DB")
    data = None
    with open("pos","r") as file:
        data = eval(file.read())
    print(len(data))