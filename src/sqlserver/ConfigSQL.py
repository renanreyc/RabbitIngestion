import pyodbc
import os

class ConfigSQL:
    def __init__(self):
            """
            Initialize BackendDatabase

            back_end_connection = BackendDatabase()

            Parameters
            ----------
            host

            Returns
            ----------
            new BackendDatabase class

            Atributes
            ----------

            """
            self.host = os.environ.get("prod_sqlserver_host", '.env')
            self.port = os.environ.get("prod_sqlserver_port", '.env')
            self.db = os.environ.get("prod_sqlserver_db", '.env')
            self.username = os.environ.get("prod_sqlserver_user")
            self.password = os.environ.get("prod_sqlserver_pw", '.env')
            self.driver = '{SQL Server}'

            self.connection_string = f'DRIVER={self.driver};SERVER={self.host}, {self.port};DATABASE={self.db};UID={self.username};PWD={self.password}'
            self.connection = pyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()

    def obter_lista_filas(self, consulta):
        cursor = self.connection.cursor()
        try:
            # Realizar a consulta para obter a lista de filas
            cursor.execute(consulta)
            rows =cursor.fetchall()
            lista_filas = [row[0] for row in rows]

            # Fechar a conexão com o banco de dados
            cursor.close()
            self.connection.close()
        except (Exception) as error:
            message_error = f"Erro ao obter lista da consulta {consulta} no sqlServer: " + \
                str(error)
            print(message_error)

            self.connection.rollback()
            cursor.close()
            raise 

        return lista_filas
    