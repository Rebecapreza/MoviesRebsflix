from http.server import BaseHTTPRequestHandler, HTTPServer
from Database import Database
from Auth import Auth
import json
import urllib.parse

# Inicializa
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
        payload = auth.verify_token(token) # Retorna payload ou None
        
        if not payload:
            return None, 401
            
        if role_required and payload.get('tipo') != role_required:
            return None, 403 # Proibido
            
        return payload, 200

    # ---- GET ----
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # Rota 1: Listar Filmes (Com filtro de busca/genero)
        if path == "/filmes":
            search = query_params.get('search', [None])[0] # Pode ser usado para busca textual
            genero = query_params.get('genero', [None])[0]
            
            # Usa o novo método complexo do Database
            movies = db.get_movies_complex(status='aprovado', search_term=search or genero)
            
            self._set_headers(200)
            self.wfile.write(json.dumps(movies, default=str).encode())
            return

        # Rota 2: Detalhes do Filme
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

        # Rota 3: Contagem de Pendentes (Para Admin/Notificações) - DO NOVO SCRIPT
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
            
        # Rota 4: Listar Pendentes (Admin) - DO NOVO SCRIPT
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
            self.handle_login(data)
            return

        # Registro
        elif self.path == "/api/register":
            status, response = auth.handle_register(body)
            self._set_headers(status)
            self.wfile.write(json.dumps(response).encode())
            return

        # Cadastro de Filme (Completo)
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
            
        # Aprovar Filme (Admin) - DO NOVO SCRIPT
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
        # Manter lógica de edição de perfil e filme existente
        # Apenas certifique-se de usar db.update_user ou similar
        # Se precisar da lógica do script novo para editar filme (com atores/diretores), 
        # você precisará criar um update_movie_complete no Database.py
        
        # Exemplo simplificado:
        if self.path.startswith("/filmes/edicao/"):
            # ... lógica de update ...
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "success", "message": "Editado (Simulação)"}).encode())
            return
            
        if self.path == "/perfil":
             # ... lógica de update perfil ...
             # Reutilize o que você já tinha no Auth.handle_profile_update se possível
             pass

    # ---- DELETE ----
    def do_DELETE(self):
        if self.path.startswith("/filmes/edicao/"):
            payload, code = self._authorize()
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

# Configuração para rodar na porta 8000 (compatível com seu Vite Proxy)
def run():
    server_addr = ('localhost', 8000)
    httpd = HTTPServer(server_addr, Server)
    print("Servidor rodando em http://localhost:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    run()