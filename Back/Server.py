import os 
import json 
import mysql.connector 

from http.server import SimpleHTTPRequestHandler , HTTPServer 
from urllib.parse import urlparse, parse_qs, urlencode 

# Conexão com o banco de dados MySQL
try:
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'senai',
        database = 'Filmes' # CRÍTICO: Banco de dados especificado
    )
except mysql.connector.Error as err:
    print(f"ERRO DE CONEXÃO COM O MYSQL: {err}")
    # Se a conexão falhar, o script terminará aqui, mostrando o erro real.
    exit(1)


class MyHandle(SimpleHTTPRequestHandler):
    
    # Método para lidar com requisições OPTIONS (CORS pre-flight)
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    # Tratamento de GET: Permite que o SimpleHTTPRequestHandler procure por arquivos estáticos.
    def do_GET(self):
        SimpleHTTPRequestHandler.do_GET(self)

    # Cadastro de novo usuário
    def new_user (self, nome, email, senha):
        cursor = mydb.cursor() 
        
        # Verificação de existência de usuário/email
        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE email = %s OR nome = %s", (email, nome)
        )
        if cursor.fetchone()[0] > 0:
            cursor.close()
            return "Nome ou e-mail já cadastrados"
        
        try:
            # Insere um novo usuário na tabela
            cursor.execute (
                "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
                (nome, email, senha)
            )
            mydb.commit()
            cursor.close()
            return "Cadastro realizado com sucesso!"
        except Exception as e:
            mydb.rollback()
            cursor.close()
            # 🚨 CRÍTICO: Loga o erro real do MySQL no terminal do Python.
            print(f"Erro no MySQL durante o cadastro: {e}") 
            return f"Erro no banco de dados: {str(e)}"

    # Lida com requisições POST para o cadastro
    def do_POST(self):
        # 🚨 ESTABILIDADE: Bloco try/except para capturar o erro 500
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Cabeçalhos CORS
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Dados JSON inválidos."}).encode('utf-8'))
                return
                
            response_data = {}
            path = urlparse(self.path).path 

            if path == '/register': # O proxy do Vite garante que o path será /register
                nome = data.get('nome')
                email = data.get('email')
                senha = data.get('senha')
                
                message = self.new_user(nome, email, senha)
                
                if "sucesso" in message:
                    self.send_response(201)
                    response_data = {"status": "success", "message": message}
                else:
                    self.send_response(400)
                    response_data = {"status": "error", "message": message}
            
            else:
                self.send_response(404)
                response_data = {"status": "error", "message": "Endpoint não encontrado."}
            
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        except Exception as e:
            # Captura a exceção interna que causou o 500 original
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": f"Erro interno do servidor: {e}"}).encode('utf-8'))
            print(f"ERRO CRÍTICO NO POST: {e}") # Loga no terminal Python
            return


# BLOCO DE INICIALIZAÇÃO DO SERVIDOR 
if __name__ == "__main__":
    PORT = 8000 
    Handler = MyHandle
    
    with HTTPServer(("", PORT), Handler) as httpd:
        print(f"Servidor Python iniciado e servindo na porta {PORT}")
        httpd.serve_forever()