from http.server import BaseHTTPRequestHandler, HTTPServer
from Database import Database
from Auth import Auth
import json

db = Database()
auth = Auth(db)

class Server(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

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

        # ---- CADASTRO ----
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

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Rota não encontrada"}).encode())


def run():
    server = ("localhost", 5000)
    httpd = HTTPServer(server, Server)
    print("Servidor rodando em http://localhost:5000")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
