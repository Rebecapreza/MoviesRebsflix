from http.server import BaseHTTPRequestHandler, HTTPServer
from Database import Database
from Auth import Auth
import json
import urllib.parse # Importado para parsear query parameters na rota GET /filmes

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

    # ---- LÓGICA DE AUTORIZAÇÃO ----
    def _authorize(self):
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return 401, {"error": "Token não fornecido ou formato inválido"}
        
        try:
            token = auth_header.split(" ")[1]
            payload = auth.verify_token(token)
            return 200, payload
        except Exception as e:
            return 401, {"error": f"Token inválido/expirado: {str(e)}"}

    # ---- BUSCA DE FILMES E DETALHES ----
    def do_GET(self):
        
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        status, payload = self._authorize()
        if status != 200:
            self._set_headers(status)
            self.wfile.write(json.dumps(payload).encode())
            return
            
        # Rota de todos os filmes 
        if path == "/filmes":
            try:
                genero = query_params.get('genero', [None])[0]
                
                movies = db.get_all_approved_movies(genero=genero) 
                
                self._set_headers(200)
                self.wfile.write(json.dumps(movies).encode()) 
                return
            except Exception as e:
                print(f"=== ERRO NO GET /filmes ===\n{e}\n=====================")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": "Erro interno ao buscar filmes"}).encode())
                return
                
        # Rota de detalhes do filme
        if path.startswith("/filme/"):
            try:
                movie_id = path.split("/")[2]
                movie = db.get_movie_by_id(movie_id)
                
                if movie:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"status": "success", "movie": movie}).encode()) 
                    return
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"status": "error", "message": "Filme não encontrado"}).encode())
                    return
                    
            except IndexError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": "ID do filme é obrigatório"}).encode())
                return
            except Exception as e:
                print(f"=== ERRO NO GET /filme/<id> ===\n{e}\n=====================")
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": "Erro interno ao buscar detalhes"}).encode())
                return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Rota não encontrada"}).encode())


    def do_POST(self):
        # ---- LOGIN ----
        if self.path == "/login":
            try:
                content_length = int(self.headers["Content-Length"])
                body = self.rfile.read(content_length).decode("utf-8")

                status, response = auth.handle_login(body)

                self._set_headers(status)
                self.wfile.write(json.dumps(response).encode())
                return

            except Exception as e:
                print("=== ERRO NO LOGIN ===")
                print(e)
                print("=====================")

                self._set_headers(500)
                self.wfile.write(json.dumps({"error": "Erro interno no servidor"}).encode())
                return

        # ---- Cadastro ----
        if self.path == "/register":
            try:
                content_length = int(self.headers["Content-Length"])
                body = self.rfile.read(content_length).decode("utf-8")

                status, response = auth.handle_register(body)

                self._set_headers(status)
                self.wfile.write(json.dumps(response).encode())
                return

            except Exception as e:
                print("=== ERRO NO CADASTRO ===")
                print(e)
                print("=========================")

                self._set_headers(500)
                self.wfile.write(json.dumps({"error": "Erro interno no servidor"}).encode())
                return

        # --- CADASTRO DE FILME (Apenas para Usuário Logado) ----
        if self.path == "/filmes/cadastro":
            status, payload = self._authorize()
            if status != 200:
                self._set_headers(status)
                self.wfile.write(json.dumps(payload).encode())
                return
                
            try:
                content_length = int(self.headers["Content-Length"])
                body = self.rfile.read(content_length).decode("utf-8")
                
                # O ID do usuário criador vem do payload do token
                status, response = auth.handle_movie_creation(body, payload["id"])
                
                self._set_headers(status)
                self.wfile.write(json.dumps(response).encode())
                return
                
            except Exception as e:
                print(f"=== ERRO NO POST /filmes/cadastro ===\n{e}\n=====================")
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": "Erro interno no cadastro de filme"}).encode())
                return


        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Rota não encontrada"}).encode())

    # ---- EDIÇÃO DE FILME E PERFIL ----
    def do_PUT(self):
        status, payload = self._authorize()
        if status != 200:
            self._set_headers(status)
            self.wfile.write(json.dumps(payload).encode())
            return
            
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._set_headers(400)
            self.wfile.write(json.dumps({"status": "error", "message": "Conteúdo vazio"}).encode())
            return
            
        body = self.rfile.read(content_length).decode("utf-8")

        # Rota de edição de filme
        if self.path.startswith("/filmes/edicao/"):
            try:
                movie_id = self.path.split("/")[3] 
                status, response = auth.handle_movie_update(movie_id, body, payload) 
                
                self._set_headers(status)
                self.wfile.write(json.dumps(response).encode())
                return
                
            except IndexError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": "ID do filme é obrigatório"}).encode())
                return
            except Exception as e:
                print(f"=== ERRO NO PUT /filmes/edicao/<id> ===\n{e}\n=====================")
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": "Erro interno na edição do filme"}).encode())
                return

        # Rota de edição de perfil
        if self.path == "/perfil":
            try:
                status, response = auth.handle_profile_update(body, payload)
                
                self._set_headers(status)
                self.wfile.write(json.dumps(response).encode())
                return
            except Exception as e:
                print(f"=== ERRO NO PUT /perfil ===\n{e}\n=====================")
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": "Erro interno na edição do perfil"}).encode())
                return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Rota não encontrada"}).encode())


    # ---- Exclusão de filme ----
    def do_DELETE(self):
        status, payload = self._authorize()
        if status != 200:
            self._set_headers(status)
            self.wfile.write(json.dumps(payload).encode())
            return
            
        # Rota de exclusão de filme
        if self.path.startswith("/filmes/edicao/"):
            try:
                movie_id = self.path.split("/")[3]
                status, response = auth.handle_movie_deletion(movie_id, payload) 
                
                self._set_headers(status)
                self.wfile.write(json.dumps(response).encode())
                return
                
            except IndexError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": "ID do filme é obrigatório"}).encode())
                return
            except Exception as e:
                print(f"=== ERRO NO DELETE /filmes/edicao/<id> ===\n{e}\n=====================")
                self._set_headers(500)
                self.wfile.write(json.dumps({"status": "error", "message": "Erro interno na exclusão do filme"}).encode())
                return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Rota não encontrada"}).encode())


def run():
    server = ("localhost", 5000)
    httpd = HTTPServer(server, Server)
    print("Servidor rodando em http://localhost:5000")
    httpd.serve_forever()


if __name__ == "__main__":
    run()