import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
import mysql.connector
from mysql.connector import Error
from decimal import Decimal
import datetime
import hashlib
import bcrypt
import jwt

# --- CONFIGURAÇÕES ---
SECRET_KEY = "123456"  # Chave secreta para o JWT
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "root", # <--- CONFIRA SUA SENHA DO BANCO AQUI
    'database': "filmes" # <--- O NOME DO SEU BANCO É 'filmes' (minúsculo)
}
PORT = 8000 # Porta que o Vite está esperando

# --- HELPER: CONVERSOR DE JSON ---
def json_converter(o):
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, datetime.timedelta):
        total_seconds = int(o.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'
    if isinstance(o, datetime.date):
        return o.strftime('%Y-%m-%d')
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

# ============================================================================
# CLASSE DATABASE (Conexão e Consultas)
# ============================================================================
class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("✅ Conectado ao MySQL com sucesso.")
        except Error as e:
            print(f"❌ Erro ao conectar ao MySQL: {e}")

    def _get_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

    # ---- AUXILIAR: Buscar ou Criar ID ----
    def get_or_create_id(self, cursor, table_name, column_name, value):
        if not value or not value.strip(): return None
        value = value.strip()
        
        if table_name.lower() in ['diretor', 'atores']:
            parts = value.split(' ', 1)
            nome = parts[0]
            sobrenome = parts[1] if len(parts) > 1 else ''
            pk_field = f"id_{table_name.lower()}"
            
            cursor.execute(f"SELECT {pk_field} FROM {table_name} WHERE nome = %s AND sobrenome = %s", (nome, sobrenome))
            result = cursor.fetchone()
            if result: return result[0]
            
            cursor.execute(f"INSERT INTO {table_name} (nome, sobrenome, genero, nacionalidade) VALUES (%s, %s, 'N/A', 'N/A')", (nome, sobrenome))
            return cursor.lastrowid
        else:
            pk_field = f"id_{table_name.lower()}" 
            if table_name == 'generos': pk_field = 'id_generos' # Ajuste plural
            
            cursor.execute(f"SELECT {pk_field} FROM {table_name} WHERE {column_name} = %s", (value,))
            result = cursor.fetchone()
            if result: return result[0]
            
            cursor.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (%s)", (value,))
            return cursor.lastrowid

    # ---- USUÁRIOS ----
    def get_user_by_email(self, email):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            return cursor.fetchone()
        except Error as e:
            print(f"Erro get_user: {e}")
            return None

    def create_user(self, nome, email, senha_hash):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo_usuario) VALUES (%s, %s, %s, 'comum')", (nome, email, senha_hash))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Erro create_user: {e}")
            return False

    def update_user(self, user_id, nome, email, senha_hash=None):
        try:
            cursor = self._get_connection().cursor()
            updates = []
            params = []
            if nome: updates.append("nome = %s"); params.append(nome)
            if email: updates.append("email = %s"); params.append(email)
            if senha_hash: updates.append("senha = %s"); params.append(senha_hash)
            
            if not updates: return False
            
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id_user = %s"
            params.append(user_id)
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except Error:
            return False

    # ---- FILMES (LEITURA) ----
    def get_movies_complex(self, status='aprovado', search_term=None):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            params = [status]
            query = """
                SELECT 
                    f.id_filme, f.titulo, f.ano, f.poster_url as poster, f.sinopse, f.tp_duracao, f.orcamento, f.status,
                    GROUP_CONCAT(DISTINCT CONCAT(d.nome, ' ', d.sobrenome) SEPARATOR ', ') as diretores,
                    GROUP_CONCAT(DISTINCT g.generos SEPARATOR ', ') as generos_str
                FROM filme f
                LEFT JOIN filme_diretor fd ON f.id_filme = fd.id_filme
                LEFT JOIN diretor d ON fd.id_diretor = d.id_diretor
                LEFT JOIN generos_filme fg ON f.id_filme = fg.id_filme
                LEFT JOIN generos g ON fg.id_generos = g.id_generos
                WHERE f.status = %s
            """
            if search_term:
                query += " AND (f.titulo LIKE %s OR g.generos LIKE %s)"
                like = f"%{search_term}%"
                params.extend([like, like])
            
            query += " GROUP BY f.id_filme ORDER BY f.id_filme DESC"
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            print(f"Erro lista filmes: {e}")
            return []

    def get_movie_by_id(self, movie_id):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            query = """
                SELECT f.*, 
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
            return cursor.fetchone()
        except Error as e:
            print(f"Erro detalhe filme: {e}")
            return None

    def get_pending_count(self):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("SELECT COUNT(id_filme) FROM filme WHERE status = 'pendente'")
            res = cursor.fetchone()
            return res[0] if res else 0
        except:
            return 0

    # ---- FILMES (ESCRITA) ----
    def create_movie(self, data, user_id, is_admin=False):
        try:
            cursor = self._get_connection().cursor()
            # self.connection.start_transaction() # Opcional se autocommit for False

            titulo = data.get('titulo')
            poster = data.get('poster_url')
            sinopse = data.get('sinopse')
            ano = data.get('ano')
            duracao = data.get('duracao', '01:30:00') or '01:30:00'
            orcamento = data.get('orcamento', 0)
            status = 'aprovado' if is_admin else 'pendente'

            cursor.execute("""
                INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, orcamento, id_user, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (titulo, sinopse, poster, ano, duracao, orcamento, user_id, status))
            id_filme = cursor.lastrowid

            if 'genero' in data and data['genero']:
                for g_nome in data['genero'].split(','):
                    id_g = self.get_or_create_id(cursor, 'generos', 'generos', g_nome)
                    if id_g: cursor.execute("INSERT INTO generos_filme (id_filme, id_generos) VALUES (%s, %s)", (id_filme, id_g))

            self.connection.commit()
            return id_filme
        except Error as e:
            # self.connection.rollback()
            print(f"Erro criar filme: {e}")
            return None

    def update_movie(self, movie_id, data):
        try:
            cursor = self._get_connection().cursor()
            
            # Lista dinâmica de updates para evitar erro se faltar campo
            fields = []
            params = []
            
            if 'titulo' in data: fields.append("titulo=%s"); params.append(data['titulo'])
            if 'ano' in data: fields.append("ano=%s"); params.append(data['ano'])
            if 'poster_url' in data: fields.append("poster_url=%s"); params.append(data['poster_url'])
            if 'duracao' in data: fields.append("tp_duracao=%s"); params.append(data['duracao'])
            if 'orcamento' in data: fields.append("orcamento=%s"); params.append(data['orcamento'])
            if 'sinopse' in data: fields.append("sinopse=%s"); params.append(data['sinopse'])
            
            if not fields: return False
            
            params.append(movie_id)
            sql = f"UPDATE filme SET {', '.join(fields)} WHERE id_filme=%s"
            
            cursor.execute(sql, params)
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Erro update filme: {e}")
            return False

    def delete_movie(self, movie_id):
        try:
            cursor = self._get_connection().cursor()
            # Limpar relacionamentos
            cursor.execute("DELETE FROM generos_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM filme_diretor WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM atores_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM produtora_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM pais_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM linguagem_filme WHERE id_filme = %s", (movie_id,))
            
            # Deletar filme
            cursor.execute("DELETE FROM filme WHERE id_filme = %s", (movie_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Erro delete filme: {e}")
            return False

    def approve_movie(self, movie_id):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("UPDATE filme SET status='aprovado' WHERE id_filme=%s", (movie_id,))
            self.connection.commit()
            return True
        except:
            return False

# ============================================================================
# CLASSE AUTH (Autenticação)
# ============================================================================
class Auth:
    def __init__(self, db):
        self.db = db

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, hashed):
        try:
            if isinstance(password, str): password = password.encode('utf-8')
            if isinstance(hashed, str): hashed = hashed.encode('utf-8')
            return bcrypt.checkpw(password, hashed)
        except Exception as e:
            print(f"Erro bcrypt: {e}")
            return False

    def generate_token(self, user_id, tipo):
        payload = {
            'id': user_id,
            'tipo': tipo,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    def verify_token(self, token):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            return None

    def handle_login(self, body):
        try:
            data = json.loads(body)
            email = data.get('email')
            senha = data.get('senha')
            user = self.db.get_user_by_email(email)

            if user:
                # Tenta verificar senha
                is_valid = self.verify_password(senha, user['senha'])
                if not is_valid:
                    # Se falhar, pode ser porque a senha no banco é texto puro antigo
                    # Tenta comparar como texto puro (Fallback para senhas legadas)
                    if senha == user['senha']:
                        print("⚠️ Aviso: Login com senha não criptografada (legado).")
                        is_valid = True
                
                if is_valid:
                    tipo = user.get('tipo_usuario', 'comum')
                    token = self.generate_token(user['id_user'], tipo)
                    return 200, {
                        'message': 'Login OK',
                        'token': token,
                        'user': {'id': user['id_user'], 'email': user['email'], 'nome': user['nome'], 'tipo': tipo}
                    }

            return 401, {'error': 'Credenciais inválidas'}
        except Exception as e:
            print(f"Erro login: {e}")
            return 500, {'error': str(e)}

    def handle_register(self, body):
        try:
            data = json.loads(body)
            if self.db.get_user_by_email(data.get('email')):
                return 409, {'error': 'Email já existe'}
            
            hashed = self.hash_password(data.get('password'))
            if self.db.create_user(data.get('nome'), data.get('email'), hashed):
                return 201, {'message': 'Criado com sucesso'}
            return 500, {'error': 'Erro ao criar'}
        except Exception as e:
            return 500, {'error': str(e)}

# ============================================================================
# CLASSE SERVER (Rotas HTTP)
# ============================================================================
# Instâncias Globais
db = Database()
auth = Auth(db)

class Server(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def _authorize(self, role_required=None):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None, 401
        
        payload = auth.verify_token(auth_header.split(' ')[1])
        if not payload: return None, 401
        if role_required and payload.get('tipo') != role_required: return None, 403
        return payload, 200

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        if path == '/filmes':
            search = query.get('search', [None])[0]
            genero = query.get('genero', [None])[0]
            movies = db.get_movies_complex(search_term=(search or genero))
            self._set_headers(200)
            self.wfile.write(json.dumps(movies, default=json_converter).encode())

        elif path.startswith('/filme/'):
            try:
                movie_id = path.split('/')[-1]
                movie = db.get_movie_by_id(movie_id)
                if movie:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({'status': 'success', 'movie': movie}, default=json_converter).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({'error': 'Filme não encontrado'}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': str(e)}).encode())

        elif path == '/filmespendentes':
            payload, code = self._authorize('admin')
            if code != 200: 
                self._set_headers(code); self.wfile.write(json.dumps({'error': 'Auth fail'}).encode()); return
            
            movies = db.get_movies_complex(status='pendente')
            self._set_headers(200)
            self.wfile.write(json.dumps(movies, default=json_converter).encode())
            
        elif path == '/pendingcount':
            payload, code = self._authorize('admin')
            if code != 200:
                self._set_headers(code); self.wfile.write(json.dumps({'error': 'Auth fail'}).encode()); return
            
            count = db.get_pending_count()
            self._set_headers(200)
            self.wfile.write(json.dumps({'count': count}).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Rota não encontrada'}).encode())

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8')
        path = self.path

        # Rota de login é /api/login para bater com seu Front
        if path == '/api/login':
            status, response = auth.handle_login(body)
            self._set_headers(status)
            self.wfile.write(json.dumps(response).encode())

        elif path == '/api/register':
            status, response = auth.handle_register(body)
            self._set_headers(status)
            self.wfile.write(json.dumps(response).encode())

        elif path == '/filmes/cadastro':
            payload, code = self._authorize()
            if code != 200: self._set_headers(code); return
            
            data = json.loads(body)
            is_admin = (payload['tipo'] == 'admin')
            movie_id = db.create_movie(data, payload['id'], is_admin)
            
            if movie_id:
                self._set_headers(201)
                self.wfile.write(json.dumps({'status': 'success', 'message': 'Filme salvo!'}).encode())
            else:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'Erro ao salvar'}).encode())

        elif path == '/aprovarfilme':
            payload, code = self._authorize('admin')
            if code != 200: self._set_headers(code); return
            
            data = json.loads(body)
            if db.approve_movie(data.get('id_filme')):
                self._set_headers(200)
                self.wfile.write(json.dumps({'message': 'Aprovado'}).encode())
            else:
                self._set_headers(400)
        else:
            self._set_headers(404)

    def do_PUT(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8')
        path = self.path

        if path.startswith('/filmes/edicao/'):
            payload, code = self._authorize() 
            if code != 200: self._set_headers(code); return
            
            movie_id = path.split('/')[-1]
            data = json.loads(body)
            if db.update_movie(movie_id, data):
                self._set_headers(200)
                self.wfile.write(json.dumps({'status': 'success', 'message': 'Editado'}).encode())
            else:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'Erro ao editar'}).encode())

        elif path == '/perfil':
            payload, code = self._authorize()
            if code != 200: self._set_headers(code); return
            
            data = json.loads(body)
            user_id = payload["id"]
            nome = data.get("nome")
            email = data.get("email")
            senha_nova = data.get("senha")
            senha_hash = None
            if senha_nova and senha_nova != "••••••••":
                senha_hash = auth.hash_password(senha_nova)
            
            if db.update_user(user_id, nome, email, senha_hash):
                self._set_headers(200)
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            else:
                self._set_headers(400)

    def do_DELETE(self):
        path = self.path
        if path.startswith('/filmes/edicao/'):
            payload, code = self._authorize('admin') # Apenas Admin pode deletar
            if code != 200: 
                self._set_headers(code)
                self.wfile.write(json.dumps({'error': 'Apenas admin'}).encode())
                return
            
            movie_id = path.split('/')[-1]
            if db.delete_movie(movie_id):
                self._set_headers(200)
                self.wfile.write(json.dumps({'status': 'success', 'message': 'Deletado'}).encode())
            else:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'Erro ao deletar'}).encode())

# --- INICIALIZAÇÃO ---
def run():
    server_addr = ('localhost', PORT)
    httpd = HTTPServer(server_addr, Server)
    print(f"🔥 Servidor rodando na porta {PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()