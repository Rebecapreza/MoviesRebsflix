from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import mysql.connector
from mysql.connector import Error
import datetime
from decimal import Decimal
import bcrypt
import jwt

# --- CONFIGURAÇÕES ---
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
                password="root", # Verificar senha do MySQL
                database="filmes"
            )
            if self.connection.is_connected():
                print("Conectado ao MySQL com sucesso.")
        except Error as e:
            print(f" Erro ao conectar ao MySQL: {e}")

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

    # ---- FILMES (LEITURA) ----
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
                query += " AND (f.titulo LIKE %s OR g.generos LIKE %s)"
                term = f"%{search_term}%"
                params.extend([term, term])

            query += " GROUP BY f.id_filme ORDER BY f.id_filme DESC"
            
            cursor.execute(query, params)
            movies = cursor.fetchall()
            
            # Formatações
            for m in movies:
                m['duracao_str'] = self._format_duration(m['tp_duracao'])
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
                movie['genero'] = movie['genero_unico'] 
                if isinstance(movie['tp_duracao'], datetime.timedelta):
                    movie['tp_duracao'] = str(movie['tp_duracao'])
                if isinstance(movie['orcamento'], Decimal):
                    movie['orcamento'] = str(movie['orcamento'])
            
            return movie
        except Error as e:
            print(f"Erro get_movie_by_id_complex: {e}")
            return None

    # ---- FILMES (ESCRITA) ----
    def create_movie_complete(self, data, user_id, is_admin=False):
        try:
            cursor = self._get_connection().cursor()
            
            # Extração de dados
            titulo = data.get('titulo')
            poster = data.get('poster_url')
            sinopse = data.get('sinopse')
            ano = data.get('ano')
            duracao_str = str(data.get('duracao', '0'))
            
            if duracao_str.isdigit():
                mins = int(duracao_str)
                duracao_fmt = f"{mins//60:02}:{mins%60:02}:00"
            else:
                duracao_fmt = "01:30:00"

            status = 'aprovado' if is_admin else 'pendente'

            # 1. Inserir Filme
            query_filme = """
                INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, id_user, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_filme, (titulo, sinopse, poster, ano, duracao_fmt, user_id, status))
            id_filme = cursor.lastrowid

            # 2. Vincular Gêneros
            if 'genero' in data and data['genero']:
                generos = [g.strip() for g in data['genero'].split(',')]
                for g_nome in generos:
                    id_g = self.get_or_create_id(cursor, 'generos', 'generos', g_nome)
                    if id_g: cursor.execute("INSERT INTO generos_filme (id_filme, id_generos) VALUES (%s, %s)", (id_filme, id_g))

            self.connection.commit()
            return id_filme

        except Error as e:
            print(f"Erro create_movie_complete: {e}")
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
        except Error as e:
            print(f"Erro update_movie: {e}")
            return False

    def delete_movie(self, movie_id):
        try:
            cursor = self._get_connection().cursor()
            # Limpa relacionamentos
            cursor.execute("DELETE FROM generos_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM filme_diretor WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM atores_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM produtora_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM pais_filme WHERE id_filme = %s", (movie_id,))
            cursor.execute("DELETE FROM linguagem_filme WHERE id_filme = %s", (movie_id,))
            
            # Deleta filme
            cursor.execute("DELETE FROM filme WHERE id_filme = %s", (movie_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Erro delete_movie: {e}")
            self.connection.rollback()
            return False

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


# CLASSE AUTH
class Auth:
    def __init__(self, database):
        self.db = database

    # ---- CRIPTOGRAFAR SENHA (bcrypt) ----
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # ---- VERIFICAR SENHA (bcrypt) ----
    def verify_password(self, password, hashed):
        try:
            if isinstance(password, str): password = password.encode("utf-8")
            if isinstance(hashed, str): hashed = hashed.encode("utf-8")
            return bcrypt.checkpw(password, hashed)
        except ValueError:
            print("Aviso: Senha no banco não é hash válido.")
            return False
        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False

    # ---- LOGIN ----
    def handle_login(self, body):
        try:
            data = json.loads(body)
            email = data.get("email")
            senha = data.get("senha")

            if not email or not senha:
                return 400, {"error": "Email e senha são obrigatórios"}

            user = self.db.get_user_by_email(email)

            if user:
                if self.verify_password(senha, user["senha"]):
                    tipo_usuario = user.get("tipo_usuario", "comum")
                    token = self.generate_token(user["id_user"], tipo_usuario)
                    return 200, {
                        "message": "Login OK",
                        "token": token,
                        "user": {
                            "id": user["id_user"],
                            "email": user["email"],
                            "nome": user["nome"],
                            "tipo": tipo_usuario 
                        }
                    }
                else:
                    return 401, {"error": "Senha incorreta"}

            return 404, {"error": "Email não encontrado"}

        except json.JSONDecodeError:
            return 400, {"error": "JSON inválido"}
        except Exception as e:
            print(f"Erro no login: {e}")
            return 500, {"error": str(e)}

    # ---- CADASTRO ----
    def handle_register(self, body):
        try:
            data = json.loads(body)
            nome = data.get("nome")
            email = data.get("email")
            senha = data.get("password") 

            if not nome or not email or not senha:
                return 400, {"error": "Dados incompletos"}

            if self.db.get_user_by_email(email):
                return 409, {"error": "Email já cadastrado"}

            senha_hash = self.hash_password(senha)
            if self.db.create_user(nome, email, senha_hash):
                return 201, {"message": "Usuário criado com sucesso!"}
            return 500, {"error": "Erro ao criar usuário"}

        except Exception as e:
            return 500, {"error": str(e)}

    # ---- PERFIL ----
    def handle_profile_update(self, body, payload):
        try:
            data = json.loads(body)
            user_id = payload["id"]
            nome = data.get("nome")
            email = data.get("email")
            senha_nova = data.get("senha")
            
            senha_hash = None
            if senha_nova and senha_nova != "••••••••": 
                senha_hash = self.hash_password(senha_nova)
            
            if self.db.update_user(user_id, nome, email, senha_hash):
                return 200, {"status": "success", "message": "Perfil atualizado"}
            return 400, {"status": "error", "message": "Erro ao atualizar"}
        except Exception as e:
            return 500, {"status": "error", "message": str(e)}

    # ---- JWT ----
    def generate_token(self, usuario_id, tipo):
        payload = {
            "id": usuario_id,
            "tipo": tipo,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
    def verify_token(self, token):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return None


# CLASSE SERVER (HTTP HANDLER)

# Instancia Globalmente
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

    # Autorização Auxiliar
    def _authorize(self, role_required=None):
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None, 401
        
        token = auth_header.split(" ")[1]
        payload = auth.verify_token(token)
        
        if not payload:
            return None, 401
            
        if role_required and payload.get('tipo') != role_required:
            return None, 403 
            
        return payload, 200

    # ---- GET ----
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # 1. Listar Filmes
        if path == "/filmes":
            search = query_params.get('search', [None])[0]
            genero = query_params.get('genero', [None])[0]
            movies = db.get_movies_complex(status='aprovado', search_term=search or genero)
            self._set_headers(200)
            self.wfile.write(json.dumps(movies, default=str).encode())
            return

        # 2. Detalhes do Filme
        if path.startswith("/filme/"):
            try:
                movie_id = path.split("/")[2]
                movie = db.get_movie_by_id_complex(movie_id)
                if movie:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"status": "success", "movie": movie}, default=str).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"status": "error", "message": "Filme não encontrado"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # 3. Contagem Pendentes (Admin)
        if path == "/pendingcount":
            payload, code = self._authorize(role_required='admin')
            if code != 200:
                self._set_headers(code)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
            count = db.get_pending_count()
            self._set_headers(200)
            self.wfile.write(json.dumps({"count": count}).encode())
            return
            
        # 4. Listar Pendentes (Admin)
        if path == "/filmespendentes":
            payload, code = self._authorize(role_required='admin')
            if code != 200:
                self._set_headers(code)
                return
            movies = db.get_movies_complex(status='pendente')
            self._set_headers(200)
            self.wfile.write(json.dumps(movies, default=str).encode())
            return

        self._set_headers(404)

    # ---- POST ----
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except:
            data = {}

        # Login
        if self.path == "/api/login": 
            status, response = auth.handle_login(body)
            self._set_headers(status)
            self.wfile.write(json.dumps(response).encode())
            return

        # Registro
        elif self.path == "/api/register":
            status, response = auth.handle_register(body)
            self._set_headers(status)
            self.wfile.write(json.dumps(response).encode())
            return

        # Cadastro de Filme
        if self.path == "/filmes/cadastro":
            payload, code = self._authorize()
            if code != 200:
                self._set_headers(code)
                self.wfile.write(json.dumps({"error": "Login necessário"}).encode())
                return
            
            is_admin = (payload.get('tipo') == 'admin')
            movie_id = db.create_movie_complete(data, payload['id'], is_admin)
            
            if movie_id:
                self._set_headers(201)
                msg = "Filme aprovado!" if is_admin else "Filme enviado para análise."
                self.wfile.write(json.dumps({"status": "success", "message": msg, "id": movie_id}).encode())
            else:
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": "Erro ao salvar"}).encode())
            return
            
        # Aprovar Filme (Admin)
        if self.path == "/aprovarfilme":
            payload, code = self._authorize(role_required='admin')
            if code != 200:
                self._set_headers(code)
                return
            movie_id = data.get('id_filme')
            if db.approve_movie(movie_id):
                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "success", "message": "Aprovado"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error"}).encode())
            return

        self._set_headers(404)

    # ---- PUT ----
    def do_PUT(self):
        # Edição de Filme
        if self.path.startswith("/filmes/edicao/"):
            payload, code = self._authorize()
            if code != 200:
                self._set_headers(code)
                return
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                movie_id = self.path.split('/')[-1]
                data = json.loads(body)
                if db.update_movie(movie_id, data):
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"status": "success", "message": "Editado"}).encode())
                else:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"status": "error", "message": "Erro ao editar"}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
            return
            
        # Edição de Perfil
        if self.path == "/perfil":
            payload, code = self._authorize()
            if code != 200: self._set_headers(code); return
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            status, response = auth.handle_profile_update(body, payload)
            
            self._set_headers(status)
            self.wfile.write(json.dumps(response).encode())
            return

    # ---- DELETE ----
    def do_DELETE(self):
        if self.path.startswith("/filmes/edicao/"):
            payload, code = self._authorize(role_required='admin')
            if code != 200:
                self._set_headers(code)
                return
            try:
                movie_id = self.path.split('/')[-1]
                if db.delete_movie(movie_id):
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"status": "success", "message": "Deletado"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"status": "error"}).encode())
            except:
                self._set_headers(500)
            return

# --- EXECUÇÃO ---
def run():
    server_addr = ('localhost', 8000)
    httpd = HTTPServer(server_addr, Server)
    print(" Servidor rodando unificado em http://localhost:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    run()