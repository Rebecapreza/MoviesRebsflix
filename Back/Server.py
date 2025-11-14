import os #Interage com o sistema de arquivos
import json #Manipula dados no formato JSON
import mysql.connector # Conecta e executa comandos SQL

from http.server import SimpleHTTPRequestHandler , HTTPServer 

from urllib.parse import urlparse, parse_qs, urlencode 

#Conexão com o banco de dados MySQL
mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'senai'
)

class MyHandle(SimpleHTTPRequestHandler):
    # Tenta abrir e servir um arquivo html, caso contrário retorna a lista padrão de diretórios
    def list_directory(self, path):
        try:
            f = open(os.path.join(path, 'index.html'), 'r')

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f.read().encode('utf-8'))
            f.close()
            return None
        except FileNotFoundError:
            pass
        return super().list_directory(path)
    
    # Usuário fixo para teste
    def fixed_user(self, user, password):
        login = 'Rebs'
        senha = '1234'

        if user == login and password == senha:
            return "Usuário logado com sucesso"
        else:
            return "Usuário ou senha inválidos"
        
    # Cadastro de novo usuário
    def new_user (self, nome, email, senha):
        cursor = mydb.cursor() # Cursos - Permite a interação com o banco de dados
        
        # Verificação de existência de usuário/email
        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE email = %s OR nome = %s", (email, nome)
        )
        if cursor.fetchone()[0] > 0:
            cursor.close()
            return "Nome ou e-mail já cadastrados"
        
        # Insere um novo usuário na tabela
        try:
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
            # Retorna o erro do MySQL para ajudar na depuração
            return f"Erro ao cadastrar: {str(e)}"
    
    # Login de usuário
    def login_user(self, usuario, senha):
        cursor = mydb.cursor()

        # Verifica se é nome ou email
        cursor.execute(
            "SELECT id_user FROM usuarios WHERE (email = %s OR nome = %s) AND senha = %s", (usuario, usuario, senha)
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            return "Usuário logado com sucesso!"
        else:
            return "Usuário ou senha incorretos"

    # 🚨 NOVO MÉTODO: Lida com requisições POST para o cadastro
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Configura CORS para permitir chamadas do front-end
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

        if self.path == '/register':
            nome = data.get('nome')
            email = data.get('email')
            senha = data.get('senha')
            
            # Chama a função de cadastro
            message = self.new_user(nome, email, senha)
            
            # Prepara a resposta baseada na mensagem
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