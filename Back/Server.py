from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import mysql.connector
from mysql.connector import Error
import datetime
from decimal import Decimal
import bcrypt
import jwt

SECRET_KEY = "1234"

# CLASSE DATABASE
class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root", # Conferir senha do MySQL 
                database="filmes"
            )
            if self.connection.is_connected():
                print("Conectado ao MySQL com sucesso.")
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")

    def _get_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection

    def _format_duration(self, timedelta_obj):
        if isinstance(timedelta_obj, datetime.timedelta):
            total_seconds = int(timedelta_obj.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02}:{minutes:02}:{seconds:02}'
        return str(timedelta_obj)

    def get_or_create_id(self, cursor, table_name, column_name, value):
        if not value or not value.strip(): return None
        value = value.strip()
        if table_name in ['Diretor', 'Ator']:
            parts = value.split(' ', 1)
            nome = parts[0]
            sobrenome = parts[1] if len(parts) > 1 else ''
            cursor.execute(f"SELECT id_{table_name.lower()} FROM {table_name} WHERE nome = %s AND sobrenome = %s", (nome, sobrenome))
            result = cursor.fetchone()
            if result: return result[0]
            cursor.execute(f"INSERT INTO {table_name} (nome, sobrenome, genero, nacionalidade) VALUES (%s, %s, 'N/A', 'N/A')", (nome, sobrenome))
            return cursor.lastrowid
        else:
            cursor.execute(f"SELECT id_{table_name.lower()} FROM {table_name} WHERE {column_name} = %s", (value,))
            result = cursor.fetchone()
            if result: return result[0]
            cursor.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (%s)", (value,))
            return cursor.lastrowid

    def get_user_by_email(self, email):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            query = "SELECT id_user, nome, email, senha, tipo_usuario FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            return cursor.fetchone()
        except Error: return None

    def create_user(self, nome, email, senha_hash, tipo='comum'):
        try:
            cursor = self._get_connection().cursor()
            query = "INSERT INTO usuarios (nome, email, senha, tipo_usuario) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nome, email, senha_hash, tipo))
            self.connection.commit()
            return True
        except Error: return False
    
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
            return cursor.rowcount > 0
        except Error: return False

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
                term = f"%{search_term}%"
                params.extend([term, term])
            query += " GROUP BY f.id_filme ORDER BY f.id_filme DESC"
            cursor.execute(query, params)
            movies = cursor.fetchall()
            for m in movies:
                m['duracao_str'] = self._format_duration(m['tp_duracao'])
                if isinstance(m['orcamento'], Decimal): m['orcamento'] = str(m['orcamento'])
                if isinstance(m['tp_duracao'], datetime.timedelta): m['tp_duracao'] = str(m['tp_duracao'])
            return movies
        except Error: return []

    def get_movie_by_id_complex(self, movie_id):
        try:
            cursor = self._get_connection().cursor(dictionary=True)
            query = """
                SELECT 
                    f.id_filme, f.titulo, f.ano, f.poster_url, f.sinopse, f.tp_duracao, f.orcamento, f.status,
                    GROUP_CONCAT(DISTINCT CONCAT(d.nome, ' ', d.sobrenome) SEPARATOR ', ') as diretor,
                    GROUP_CONCAT(DISTINCT CONCAT(a.nome, ' ', a.sobrenome) SEPARATOR ', ') as atores,
                    GROUP_CONCAT(DISTINCT g.generos SEPARATOR ', ') as genero_unico
                FROM filme f
                LEFT JOIN filme_diretor fd ON f.id_filme = fd.id_filme
                LEFT JOIN diretor d ON fd.id_diretor = d.id_diretor
                LEFT JOIN atores_filme fa ON f.id_filme = fa.id_filme
                LEFT JOIN atores a ON fa.id_atores = a.id_atores
                LEFT JOIN generos_filme fg ON f.id_filme = fg.id_filme
                LEFT JOIN generos g ON fg.id_generos = g.id_generos
                WHERE f.id_filme = %s
                GROUP BY f.id_filme
            """
            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()
            if movie:
                movie['duracao'] = self._format_duration(movie['tp_duracao'])
                movie['genero'] = movie['genero_unico']
                if isinstance(movie['tp_duracao'], datetime.timedelta): movie['tp_duracao'] = str(movie['tp_duracao'])
                if isinstance(movie['orcamento'], Decimal): movie['orcamento'] = str(movie['orcamento'])
            return movie
        except Error: return None

    def create_movie_complete(self, data, user_id, is_admin=False):
        try:
            cursor = self._get_connection().cursor()
            titulo = data.get('titulo')
            poster = data.get('poster_url')
            sinopse = data.get('sinopse')
            ano = data.get('ano')
            duracao_str = str(data.get('duracao', '0'))
            if duracao_str.isdigit():
                mins = int(duracao_str)
                duracao_fmt = f"{mins//60:02}:{mins%60:02}:00"
            else: duracao_fmt = "01:30:00"
            status = 'aprovado' if is_admin else 'pendente'
            query_filme = "INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, id_user, status) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query_filme, (titulo, sinopse, poster, ano, duracao_fmt, user_id, status))
            id_filme = cursor.lastrowid
            if 'genero' in data and data['genero']:
                generos = [g.strip() for g in data['genero'].split(',')]
                for g_nome in generos:
                    id_g = self.get_or_create_id(cursor, 'generos', 'generos', g_nome)
                    if id_g: cursor.execute("INSERT INTO generos_filme (id_filme, id_generos) VALUES (%s, %s)", (id_filme, id_g))
            self.connection.commit()
            return id_filme
        except Error as e:
            if self.connection: self.connection.rollback()
            return None

    def update_movie(self, movie_id, data):
        try:
            cursor = self._get_connection().cursor()
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
        except Error: return False

    def delete_movie(self, movie_id):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("DELETE FROM generos_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM filme_diretor WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM atores_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM produtora_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM pais_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM linguagem_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM filme WHERE id_filme = %s", (movie_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error:
            self.connection.rollback()
            return False

    def get_pending_count(self):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("SELECT COUNT(id_filme) FROM filme WHERE status = 'pendente'")
            return cursor.fetchone()[0]
        except Error: return 0

    def approve_movie(self, movie_id):
        try:
            cursor = self._get_connection().cursor()
            cursor.execute("UPDATE filme SET status = 'aprovado' WHERE id_filme = %s", (movie_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error: return False

# CLASSE AUTH
class Auth:
    def __init__(self, database):
        self.db = database

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password, stored_value):
        try:
            # 1. Tenta verificar como Hash Bcrypt padrão
            password_bytes = password.encode("utf-8") if isinstance(password, str) else password
            stored_bytes = stored_value.encode("utf-8") if isinstance(stored_value, str) else stored_value
            return bcrypt.checkpw(password_bytes, stored_bytes)
        except (ValueError, Exception):
            # 2. Se falhar (ex: "Invalid Salt" pq é texto puro), compara direto
            print(f"Aviso: Senha no banco não é hash válido. Tentando comparação simples.")
            return password == stored_value

    def handle_login(self, body):
        try:
            data = json.loads(body)
            email = data.get("email")
            senha = data.get("senha")
            if not email or not senha: return 400, {"error": "Dados incompletos"}

            user = self.db.get_user_by_email(email)
            if user:
                # Verifica a senha (hash ou texto puro)
                if self.verify_password(senha, user["senha"]):
                    tipo = user.get("tipo_usuario", "comum")
                    token = self.generate_token(user["id_user"], tipo)
                    return 200, {
                        "message": "Login OK",
                        "token": token,
                        "user": {"id": user["id_user"], "email": user["email"], "nome": user["nome"], "tipo": tipo}
                    }
                else: return 401, {"error": "Senha incorreta"}
            return 404, {"error": "Email não encontrado"}
        except Exception as e: return 500, {"error": str(e)}

    def handle_register(self, body):
        try:
            data = json.loads(body)
            nome = data.get("nome")
            email = data.get("email")
            senha = data.get("password") 
            if not nome or not email or not senha: return 400, {"error": "Dados incompletos"}
            if self.db.get_user_by_email(email): return 409, {"error": "Email já cadastrado"}

            # No registro, salvamos como hash seguro
            hashed = self.hash_password(senha)
            if self.db.create_user(nome, email, hashed, 'comum'):
                return 201, {"message": "Sucesso"}
            return 500, {"error": "Erro no banco"}
        except Exception as e: return 500, {"error": str(e)}

    def handle_profile_update(self, body, payload):
        try:
            data = json.loads(body)
            senha_hash = self.hash_password(data.get("senha")) if data.get("senha") and data.get("senha") != "••••••••" else None
            if self.db.update_user(payload["id"], data.get("nome"), data.get("email"), senha_hash):
                return 200, {"status": "success", "message": "Atualizado"}
            return 400, {"status": "error", "message": "Erro"}
        except Exception as e: return 500, {"status": "error", "message": str(e)}

    def generate_token(self, uid, tipo):
        payload = {"id": uid, "tipo": tipo, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
    def verify_token(self, token):
        try: return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except: return None

# CLASSE SERVER
db = Database()
auth = Auth(db)

class Server(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE") 
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def _authorize(self, role_required=None):
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "): return None, 401
        payload = auth.verify_token(auth_header.split(" ")[1])
        if not payload: return None, 401
        if role_required and payload.get('tipo') != role_required: return None, 403
        return payload, 200

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        q = urllib.parse.parse_qs(parsed.query)

        if path == "/filmes":
            search = q.get('search', [None])[0]
            genero = q.get('genero', [None])[0]
            movies = db.get_movies_complex(status='aprovado', search_term=search or genero)
            self._set_headers(200); self.wfile.write(json.dumps(movies, default=str).encode()); return

        if path.startswith("/filme/"):
            mid = path.split("/")[2]
            movie = db.get_movie_by_id_complex(mid)
            if movie: self._set_headers(200); self.wfile.write(json.dumps({"status": "success", "movie": movie}, default=str).encode())
            else: self._set_headers(404); self.wfile.write(json.dumps({"error": "Não encontrado"}).encode())
            return

        if path == "/pendingcount":
            p, c = self._authorize('admin')
            if c!=200: self._set_headers(c); return
            self._set_headers(200); self.wfile.write(json.dumps({"count": db.get_pending_count()}).encode()); return

        if path == "/filmespendentes":
            p, c = self._authorize('admin')
            if c!=200: self._set_headers(c); return
            self._set_headers(200); self.wfile.write(json.dumps(db.get_movies_complex(status='pendente'), default=str).encode()); return

        self._set_headers(404)

    def do_POST(self):
        ln = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(ln).decode('utf-8')
        try: data = json.loads(body)
        except: data = {}

        if self.path == "/api/login":
            s, r = auth.handle_login(body)
            self._set_headers(s); self.wfile.write(json.dumps(r).encode()); return

        if self.path == "/api/register":
            s, r = auth.handle_register(body)
            self._set_headers(s); self.wfile.write(json.dumps(r).encode()); return

        if self.path == "/filmes/cadastro":
            p, c = self._authorize()
            if c!=200: self._set_headers(c); return
            is_adm = (p.get('tipo') == 'admin')
            mid = db.create_movie_complete(data, p['id'], is_adm)
            if mid:
                self._set_headers(201); self.wfile.write(json.dumps({"status": "success", "id": mid}).encode())
            else: self._set_headers(500)
            return

        if self.path == "/aprovarfilme":
            p, c = self._authorize('admin')
            if c!=200: self._set_headers(c); return
            if db.approve_movie(data.get('id_filme')): self._set_headers(200); self.wfile.write(json.dumps({"success": True}).encode())
            else: self._set_headers(400)
            return

        self._set_headers(404)

    def do_PUT(self):
        if self.path.startswith("/filmes/edicao/"):
            p, c = self._authorize()
            if c!=200: self._set_headers(c); return
            ln = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(ln).decode('utf-8')
            if db.update_movie(self.path.split('/')[-1], json.loads(body)):
                self._set_headers(200); self.wfile.write(json.dumps({"status": "success"}).encode())
            else: self._set_headers(500)
            return

        if self.path == "/perfil":
            p, c = self._authorize()
            if c!=200: self._set_headers(c); return
            ln = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(ln).decode('utf-8')
            s, r = auth.handle_profile_update(body, p)
            self._set_headers(s); self.wfile.write(json.dumps(r).encode()); return

    def do_DELETE(self):
        if self.path.startswith("/filmes/edicao/"):
            p, c = self._authorize('admin')
            if c!=200: self._set_headers(c); return
            if db.delete_movie(self.path.split('/')[-1]):
                self._set_headers(200); self.wfile.write(json.dumps({"status": "success"}).encode())
            else: self._set_headers(500)
            return

def run():
    server_addr = ('localhost', 8000)
    httpd = HTTPServer(server_addr, Server)
    print(" Servidor rodando em http://localhost:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    run()