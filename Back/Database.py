import mysql.connector
from mysql.connector import Error
import bcrypt

class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="Filmes"
            )
            if self.connection.is_connected():
                print("Conectado ao MySQL com sucesso.")
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")


    # ---- GET USUÁRIO COMUM ----
    def get_user_by_email(self, email):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id_user, nome, email, senha FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            return cursor.fetchone()
        except Error as e:
            print(f"Erro no get_user_by_email: {e}")
            return None

    # ---- GET ADMIN ----
    def get_admin_by_email(self, email):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id_adm, email, senha FROM administradores WHERE email = %s"
            cursor.execute(query, (email,))
            return cursor.fetchone()
        except Error as e:
            print(f"Erro no get_admin_by_email: {e}")
            return None

    # ---- CRIAR USUÁRIO (CADASTRO) ----
    def create_user(self, nome, email, senha_hash):
        try:
            cursor = self.connection.cursor()

            query = """
            INSERT INTO usuarios (nome, email, senha)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (nome, email, senha_hash))
            self.connection.commit()
            return True

        except Error as e:
            print(f"Erro no create_user: {e}")
            return False

    # ---- CRIAR ADMIN ----
    def create_admin(self, email, senha_hash):
        try:
            cursor = self.connection.cursor()

            query = """
            INSERT INTO administradores (email, senha)
            VALUES (%s, %s)
            """
            cursor.execute(query, (email, senha_hash))
            self.connection.commit()
            return True

        except Error as e:
            print(f"Erro no create_admin: {e}")
            return False


