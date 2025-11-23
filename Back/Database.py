import mysql.connector
from mysql.connector import Error
import bcrypt
import math # Adicionado para formatação de duração

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
            
    # ---- NOVO: ATUALIZAR USUÁRIO (PARA /perfil) ----
    def update_user(self, user_id, nome, email, senha_hash=None):
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []
            
            if nome:
                updates.append("nome = %s")
                params.append(nome)
            if email:
                updates.append("email = %s")
                params.append(email)
            if senha_hash:
                updates.append("senha = %s")
                params.append(senha_hash)

            if not updates:
                return False 

            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id_user = %s"
            params.append(user_id)
            
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0

        except Error as e:
            print(f"Erro no update_user: {e}")
            return False

    # ---- NOVO: CRIAÇÃO BÁSICA DE FILME ----
    def create_movie_base(self, titulo, sinopse, poster_url, ano, user_id, tp_duracao='01:30:00'):
        try:
            cursor = self.connection.cursor()

            query = """
            INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, id_user, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pendente')
            """
            cursor.execute(query, (titulo, sinopse, poster_url, ano, tp_duracao, user_id))
            self.connection.commit()
            return cursor.lastrowid

        except Error as e:
            print(f"Erro no create_movie_base: {e}")
            return None
            
    # ---- NOVO: ATUALIZAÇÃO BÁSICA DE FILME ----
    def update_movie_base(self, movie_id, data):
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []
            
            if 'titulo' in data and data['titulo']:
                updates.append("titulo = %s")
                params.append(data['titulo'])
            if 'sinopse' in data and data['sinopse']:
                updates.append("sinopse = %s")
                params.append(data['sinopse'])
            if 'poster_url' in data and data['poster_url']:
                updates.append("poster_url = %s")
                params.append(data['poster_url'])
            if 'ano' in data and data['ano']:
                updates.append("ano = %s")
                params.append(data['ano'])
            
            if not updates:
                return False

            query = f"UPDATE filme SET {', '.join(updates)} WHERE id_filme = %s"
            params.append(movie_id)
            
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0

        except Error as e:
            print(f"Erro no update_movie_base: {e}")
            return False

    # ---- NOVO: DELEÇÃO DE FILME ----
    def delete_movie(self, movie_id):
        try:
            cursor = self.connection.cursor()
            # 🚨 No MySQL, você deve deletar primeiro das tabelas de relacionamento (FK)
            # Para simplificar, vamos deletar as mais importantes (generos_filme e filme)
            
            cursor.execute("DELETE FROM generos_filme WHERE id_filme = %s", (movie_id,))
            
            query = "DELETE FROM filme WHERE id_filme = %s"
            cursor.execute(query, (movie_id,))
            self.connection.commit()
            return cursor.rowcount > 0

        except Error as e:
            print(f"Erro no delete_movie: {e}")
            return False
            
    # ---- NOVO: OBTER TODOS OS FILMES APROVADOS COM GÊNEROS (PARA HOME) ----
    def get_all_approved_movies(self, genero=None):
        try:
            base_query = """
                SELECT f.id_filme, f.titulo, f.sinopse, f.poster_url AS poster, f.ano, TIME_TO_SEC(f.tp_duracao) AS duracao_sec
                FROM filme f
            """
            
            where_clauses = ["f.status = 'aprovado'"]
            join_clause = ""
            params = []

            if genero:
                join_clause = """
                    JOIN generos_filme gf ON f.id_filme = gf.id_filme
                    JOIN generos g ON gf.id_generos = g.id_generos
                """
                where_clauses.append("g.generos = %s")
                params.append(genero)
                
            query = base_query + join_clause
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            movies = cursor.fetchall()
            
            for movie in movies:
                movie["generos_str"] = self.get_genres_string_by_movie_id(movie["id_filme"])
                movie["duracao_str"] = self._format_duration(movie.pop("duracao_sec", None))
                
            return movies
            
        except Error as e:
            print(f"Erro no get_all_approved_movies: {e}")
            return []

    # ---- NOVO: OBTER FILME POR ID (PARA DETALHES/EDIÇÃO) ----
    def get_movie_by_id(self, movie_id):
        try:
            query = """
                SELECT id_filme, titulo, sinopse, poster_url, ano, tp_duracao, status
                FROM filme 
                WHERE id_filme = %s
            """
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()
            
            if movie:
                genres_str = self.get_genres_string_by_movie_id(movie["id_filme"])
                movie["genero"] = genres_str 
                
                # Formata a duração
                if movie["tp_duracao"]:
                     # Converte o objeto timedelta/time para string formatada
                     total_seconds = movie["tp_duracao"].total_seconds() if hasattr(movie["tp_duracao"], 'total_seconds') else (movie["tp_duracao"].hour * 3600 + movie["tp_duracao"].minute * 60 + movie["tp_duracao"].second)
                     movie["duracao"] = self._format_duration(int(total_seconds))
                else:
                    movie["duracao"] = "N/A"
                
                movie["genero_unico"] = genres_str.split(', ')[0] if genres_str else "" 

            return movie
            
        except Error as e:
            print(f"Erro no get_movie_by_id: {e}")
            return None

    # ---- NOVO: FUNÇÃO AUXILIAR PARA OBTER GÊNEROS POR ID DO FILME (COMO STRING) ----
    def get_genres_string_by_movie_id(self, movie_id):
        try:
            cursor = self.connection.cursor(dictionary=False)
            query = """
                SELECT g.generos 
                FROM generos g
                JOIN generos_filme gf ON g.id_generos = gf.id_generos
                WHERE gf.id_filme = %s
            """
            cursor.execute(query, (movie_id,))
            genres = [row[0] for row in cursor.fetchall()]
            return ", ".join(genres)
        except Error as e:
            print(f"Erro no get_genres_string_by_movie_id: {e}")
            return ""

    # ---- NOVO: FUNÇÃO AUXILIAR PARA FORMATAR DURAÇÃO (SEGUNDOS -> STRING) ----
    def _format_duration(self, total_seconds):
        if total_seconds is None or total_seconds == 0:
            return "N/A"
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h{minutes}m"
        return f"{minutes}m"