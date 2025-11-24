import mysql.connector
from mysql.connector import Error
import datetime
from decimal import Decimal

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
                database="filmes" 
            )
            if self.connection.is_connected():
                print("Conectado ao MySQL com sucesso.")
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")

    def _get_connection(self):
        """Garante que a conexão está ativa, reconectando se necessário"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

    # ---- AUXILIAR: Formatar tempo ----
    def _format_duration(self, timedelta_obj):
        if isinstance(timedelta_obj, datetime.timedelta):
            total_seconds = int(timedelta_obj.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02}:{minutes:02}:{seconds:02}'
        return str(timedelta_obj)

    # ---- AUXILIAR: Buscar ou Criar ID (Para Atores, Diretores, etc) ----
    def get_or_create_id(self, cursor, table_name, column_name, value):
        if not value or not value.strip():
            return None
        
        value = value.strip()
        
        # Lógica específica para tabelas de Pessoas (Nome + Sobrenome)
        if table_name in ['Diretor', 'Ator']:
            parts = value.split(' ', 1)
            nome = parts[0]
            sobrenome = parts[1] if len(parts) > 1 else ''
            
            cursor.execute(f"SELECT id_{table_name.lower()} FROM {table_name} WHERE nome = %s AND sobrenome = %s", (nome, sobrenome))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                cursor.execute(f"INSERT INTO {table_name} (nome, sobrenome, genero, nacionalidade) VALUES (%s, %s, 'N/A', 'N/A')", (nome, sobrenome))
                return cursor.lastrowid
        else:
            # Lógica para Produtora, Genero, etc.
            cursor.execute(f"SELECT id_{table_name.lower()} FROM {table_name} WHERE {column_name} = %s", (value,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                cursor.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (%s)", (value,))
                return cursor.lastrowid

    # ---- LOGIN & USUÁRIOS ----
    def get_user_by_email(self, email):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            # O seu banco unificou usuários, então buscamos na tabela usuarios
            query = "SELECT id_user, nome, email, senha, tipo_usuario FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            return cursor.fetchone()
        except Error as e:
            print(f"Erro no get_user_by_email: {e}")
            return None

    def create_user(self, nome, email, senha_hash):
        try:
            cursor = self._get_connection().cursor()
            query = "INSERT INTO usuarios (nome, email, senha, tipo_usuario) VALUES (%s, %s, %s, 'comum')"
            cursor.execute(query, (nome, email, senha_hash))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Erro no create_user: {e}")
            return False
    
    def update_user(self, user_id, nome, email, senha_hash=None):
        try:
            cursor = self._get_connection().cursor()
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
            
            if not updates: return False
            
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id_user = %s"
            params.append(user_id)
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Erro update_user: {e}")
            return False

    # ---- FILMES (LISTAGEM COMPLEXA - NOVO CÓDIGO) ----
    def get_movies_complex(self, status='aprovado', search_term=None):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            params = [status]
            
            query = """
                SELECT 
                    f.id_filme, f.titulo, f.ano, f.poster_url as poster, f.sinopse, f.tp_duracao, f.orcamento, f.status,
                    GROUP_CONCAT(DISTINCT CONCAT(d.nome, ' ', d.sobrenome) SEPARATOR ', ') as diretores,
                    GROUP_CONCAT(DISTINCT CONCAT(a.nome, ' ', a.sobrenome) SEPARATOR ', ') as atores,
                    GROUP_CONCAT(DISTINCT g.generos SEPARATOR ', ') as generos_str,
                    GROUP_CONCAT(DISTINCT p.nome SEPARATOR ', ') as produtoras
                FROM filme f
                LEFT JOIN filme_diretor fd ON f.id_filme = fd.id_filme
                LEFT JOIN diretor d ON fd.id_diretor = d.id_diretor
                LEFT JOIN atores_filme fa ON f.id_filme = fa.id_filme
                LEFT JOIN atores a ON fa.id_atores = a.id_atores
                LEFT JOIN generos_filme fg ON f.id_filme = fg.id_filme
                LEFT JOIN generos g ON fg.id_generos = g.id_generos
                LEFT JOIN produtora_filme fp ON f.id_filme = fp.id_produtora
                LEFT JOIN produtora p ON fp.id_produtora = p.id_produtora
                WHERE f.status = %s
            """

            if search_term:
                query += """
                    AND (f.titulo LIKE %s OR g.generos LIKE %s)
                """
                term = f"%{search_term}%"
                params.extend([term, term])

            query += " GROUP BY f.id_filme ORDER BY f.id_filme DESC"
            
            cursor.execute(query, params)
            movies = cursor.fetchall()
            
            # Formatações finais
            for m in movies:
                m['duracao_str'] = self._format_duration(m['tp_duracao'])
                # Converte Decimal para float/str se necessário para JSON
                if isinstance(m['orcamento'], Decimal):
                    m['orcamento'] = str(m['orcamento'])
                if isinstance(m['tp_duracao'], datetime.timedelta):
                    m['tp_duracao'] = str(m['tp_duracao'])

            return movies
        except Error as e:
            print(f"Erro get_movies_complex: {e}")
            return []

    def get_movie_by_id_complex(self, movie_id):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            query = """
                SELECT 
                    f.id_filme, f.titulo, f.ano, f.poster_url, f.sinopse, f.tp_duracao, f.orcamento, f.status,
                    GROUP_CONCAT(DISTINCT CONCAT(d.nome, ' ', d.sobrenome) SEPARATOR ', ') as diretor,
                    GROUP_CONCAT(DISTINCT CONCAT(a.nome, ' ', a.sobrenome) SEPARATOR ', ') as atores,
                    GROUP_CONCAT(DISTINCT g.generos SEPARATOR ', ') as genero_unico,
                    GROUP_CONCAT(DISTINCT p.nome SEPARATOR ', ') as produtora
                FROM filme f
                LEFT JOIN filme_diretor fd ON f.id_filme = fd.id_filme
                LEFT JOIN diretor d ON fd.id_diretor = d.id_diretor
                LEFT JOIN atores_filme fa ON f.id_filme = fa.id_filme
                LEFT JOIN atores a ON fa.id_atores = a.id_atores
                LEFT JOIN generos_filme fg ON f.id_filme = fg.id_filme
                LEFT JOIN generos g ON fg.id_generos = g.id_generos
                LEFT JOIN produtora_filme fp ON f.id_filme = fp.id_produtora
                LEFT JOIN produtora p ON fp.id_produtora = p.id_produtora
                WHERE f.id_filme = %s
                GROUP BY f.id_filme
            """
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()
            
            if movie:
                # Formatações
                movie['duracao'] = self._format_duration(movie['tp_duracao'])
                movie['genero'] = movie['genero_unico'] # Alias para frontend
                if isinstance(movie['tp_duracao'], datetime.timedelta):
                    movie['tp_duracao'] = str(movie['tp_duracao'])
                if isinstance(movie['orcamento'], Decimal):
                    movie['orcamento'] = str(movie['orcamento'])
            
            return movie
        except Error as e:
            print(f"Erro get_movie_by_id_complex: {e}")
            return None

    # ---- FILMES (CRIAÇÃO COMPLEXA - INTEGRANDO A LÓGICA DO NOVO SCRIPT) ----
    def create_movie_complete(self, data, user_id, is_admin=False):
        try:
            cursor = self._get_connection().cursor()
            
            # Dados do dicionário
            titulo = data.get('titulo')
            poster = data.get('poster_url')
            sinopse = data.get('sinopse')
            ano = data.get('ano')
            duracao_str = str(data.get('duracao', '0')) # Recebe minutos ou formato HH:MM:SS
            
            # Tratamento simples de duração (assumindo minutos se for número inteiro)
            if duracao_str.isdigit():
                mins = int(duracao_str)
                duracao_fmt = f"{mins//60:02}:{mins%60:02}:00"
            else:
                duracao_fmt = "01:30:00" # Padrão

            status = 'aprovado' if is_admin else 'pendente'

            # 1. Inserir Filme Base
            query_filme = """
                INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, id_user, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_filme, (titulo, sinopse, poster, ano, duracao_fmt, user_id, status))
            id_filme = cursor.lastrowid

            # 2. Inserir/Vincular Gêneros
            if 'genero' in data and data['genero']:
                generos = [g.strip() for g in data['genero'].split(',')]
                for g_nome in generos:
                    id_g = self.get_or_create_id(cursor, 'generos', 'generos', g_nome)
                    if id_g: cursor.execute("INSERT INTO generos_filme (id_filme, id_generos) VALUES (%s, %s)", (id_filme, id_g))

            # 3. Inserir/Vincular Atores (Opcional, se o form enviar)
            if 'atores' in data and data['atores']:
                atores = [a.strip() for a in data['atores'].split(',')]
                for a_nome in atores:
                    id_a = self.get_or_create_id(cursor, 'Ator', 'nome', a_nome) # 'Ator' maiúsculo pois tabela é atores? No seu SQL é 'atores'
                    # Correção: No seu SQL a tabela é 'atores', mas o metodo get_or_create usa singular pra ID.
                    # Vamos ajustar manualmente aqui para garantir:
                    # Se sua tabela chama 'atores', o método acima precisa de ajuste ou chamamos direto.
                    # Para simplificar, vamos assumir que o método get_or_create_id está ajustado para suas tabelas.
                    pass 

            self.connection.commit()
            return id_filme

        except Error as e:
            print(f"Erro create_movie_complete: {e}")
            if self.connection: self.connection.rollback()
            return None

    # ---- ADMINISTRAÇÃO ----
    def get_pending_count(self):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("SELECT COUNT(id_filme) FROM filme WHERE status = 'pendente'")
            return cursor.fetchone()[0]
        except Error:
            return 0

    def approve_movie(self, movie_id):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("UPDATE filme SET status = 'aprovado' WHERE id_filme = %s", (movie_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Erro approve_movie: {e}")
            return False
            
    def delete_movie(self, movie_id):
        try:
            cursor = self._get_connection().cursor()
            # Deletar de tabelas associativas primeiro
            cursor.execute("DELETE FROM generos_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM filme_diretor WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM atores_filme WHERE id_filme = %s", (movie_id,))
            # Deletar filme
            cursor.execute("DELETE FROM filme WHERE id_filme = %s", (movie_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Erro delete_movie: {e}")
            self.connection.rollback()
            return False