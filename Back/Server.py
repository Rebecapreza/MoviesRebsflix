from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
from urllib.parse import urlparse, parse_qs
import Database as db
import Auth

class MyAPIHandler(BaseHTTPRequestHandler):

    def _send_response(self, status_code, body=None, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()
        
        if body is not None:
            self.wfile.write(json.dumps(body).encode('utf-8'))

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return {}
            post_data = self.rfile.read(content_length)
            return json.loads(post_data)
        except Exception as e:
            print(f"Erro ao ler JSON: {e}")
            return None

    def _get_auth_user(self):
        auth_header = self.headers.get('Authorization')
        return Auth.get_user_from_token(auth_header)

    def do_OPTIONS(self):
        self._send_response(204)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        # 🚨 CRÍTICO: Rota para detalhes do filme (/filmes/:id)
        filme_id_match = re.match(r'/filmes/(\d+)$', path) 

        if path == '/filmes':
            # Rota de listagem e filtro
            titulo = query_params.get('titulo', [None])[0]
            ano = query_params.get('ano', [None])[0]
            genero = query_params.get('genero', [None])[0]
            
            # Se for apenas listagem, os params serão None e a busca trará todos aprovados.
            filmes = db.get_all_filmes(titulo, ano, genero)
            self._send_response(200, filmes)
            
        elif filme_id_match:
            # Rota para detalhes do filme (/filmes/:id)
            filme_id = int(filme_id_match.group(1))
            filme = db.get_filme_by_id(filme_id)
            if filme:
                self._send_response(200, filme)
            else:
                self._send_response(404, {'error': 'Filme não encontrado'})
        
        elif path == '/generos':
            # Rota para buscar a lista de gêneros (para o FilterModal)
            try:
                generos = db.get_all_generos()
                self._send_response(200, generos)
            except Exception as e:
                self._send_response(500, {'error': str(e)})
        
        elif path == '/anos':
            # Rota para buscar a lista de anos (para o FilterModal)
            try:
                anos = db.get_all_anos()
                self._send_response(200, anos)
            except Exception as e:
                self._send_response(500, {'error': str(e)})

        elif path == '/filmes/pending':
            # Rota para filmes pendentes (apenas ADM)
            user = self._get_auth_user()
            if not user or user.get('tipo_usuario') != 'Administrador':
                self._send_response(403, {'error': 'Acesso negado'})
                return
            filmes = db.get_pending_filmes()
            self._send_response(200, filmes)
            
        else:
            self._send_response(404, {'error': 'Endpoint não encontrado'})

    def do_POST(self):
        # Rota de Logout (não precisa de body)
        if self.path == '/logout':
            auth_header = self.headers.get('Authorization')
            if Auth.handle_logout(auth_header):
                self._send_response(200, {'message': 'Logout bem-sucedido'})
            else:
                self._send_response(400, {'error': 'Token inválido'})
            return 

        # Rota de Aprovação de Filme (não precisa de body)
        approve_match = re.match(r'/filmes/approve/(\d+)$', self.path)
        if approve_match:
            user = self._get_auth_user()
            if not user or user.get('tipo_usuario') != 'Administrador':
                self._send_response(403, {'error': 'Acesso negado'})
                return
                
            filme_id = int(approve_match.group(1))
            db.approve_filme(filme_id)
            self._send_response(200, {'message': 'Filme aprovado'})
            return 

        # Rotas que precisam de body
        data = self._read_json_body()
        if data is None:
            self._send_response(400, {'error': 'Corpo da requisição inválido ou vazio'})
            return

        if self.path == '/register':
            try:
                user = Auth.handle_register(data['nome'], data['email'], data['password']) 
                if user:
                    self._send_response(201, user)
                else:
                    self._send_response(409, {'error': 'Email já cadastrado'})
            except KeyError:
                self._send_response(400, {'error': 'Campos ausentes: nome, email, password'})

        elif self.path == '/login':
            try:
                session = Auth.handle_login(data['email'], data['password'])
                if session:
                    self._send_response(200, session)
                else:
                    self._send_response(401, {'error': 'Email ou senha inválidos'})
            except KeyError:
                self._send_response(400, {'error': 'Campos ausentes: email, password'})

        elif self.path == '/filmes':
            user = self._get_auth_user()
            if not user:
                self._send_response(401, {'error': 'Não autorizado'})
                return

            filme_id = db.create_filme(data, user['id_usuario']) 
            if filme_id:
                self._send_response(201, {'id_filme': filme_id, 'status': 'Pendente_Adicao', 'message': 'Filme enviado para aprovação.'})
            else:
                self._send_response(500, {'error': 'Falha ao criar filme'})
            
        else:
            self._send_response(404, {'error': 'Endpoint não encontrado'})

    def do_PUT(self):
        filme_id_match = re.match(r'/filmes/(\d+)$', self.path)
        
        if not filme_id_match:
            if self.path == '/perfil':
                # NOTA: Lógica de atualização de perfil não foi totalmente fornecida no db.py,
                # mas você pode adicionar db.update_user_profile(user_id, data) aqui.
                # Por enquanto, retorna 404.
                self._send_response(404, {'error': 'Endpoint de perfil PUT não implementado'})
                return
            
            self._send_response(404, {'error': 'Endpoint de filme não encontrado'})
            return

        user = self._get_auth_user()
        if not user:
            self._send_response(401, {'error': 'Não autorizado'})
            return
            
        data = self._read_json_body()
        if data is None:
            self._send_response(400, {'error': 'Corpo da requisição inválido'})
            return
            
        filme_id = int(filme_id_match.group(1))
        
        filme = db.get_filme_by_id(filme_id)
        if not filme:
            self._send_response(404, {'error': 'Filme não encontrado'})
            return

        if user.get('tipo_usuario') == 'Administrador':
            db.update_filme_admin(filme_id, data)
            self._send_response(200, {'id_filme': filme_id, 'status': 'Aprovado', 'message': 'Filme atualizado por Administrador.'})
        
        # 🚨 CRÍTICO: Correção para a chave id_usuario
        elif user.get('tipo_usuario') == 'Comum' and filme.get('id_usuario') == user.get('id_usuario'): 
            db.update_filme_comum(filme_id, data)
            self._send_response(200, {'id_filme': filme_id, 'status': 'Pendente_Edicao', 'message': 'Filme atualizado e enviado para re-aprovação.'})
        
        else:
            self._send_response(403, {'error': 'Você não tem permissão para editar este filme'})

    def do_DELETE(self):
        filme_id_match = re.match(r'/filmes/(\d+)$', self.path)
        
        if not filme_id_match:
            self._send_response(404, {'error': 'Endpoint não encontrado'})
            return

        user = self._get_auth_user()
        if not user or user.get('tipo_usuario') != 'Administrador':
            self._send_response(403, {'error': 'Acesso negado. Apenas administradores podem deletar filmes.'})
            return
            
        filme_id = int(filme_id_match.group(1))
        
        # db.delete_filme retorna o ID do último deletado (ou None/0)
        delete_result = db.delete_filme(filme_id)
        
        if delete_result is not None:
             self._send_response(200, {'message': 'Filme deletado com sucesso'})
        else:
             self._send_response(404, {'error': 'Falha ao deletar (Filme não encontrado ou erro de DB).'})

def run(server_class=HTTPServer, handler_class=MyAPIHandler, port=8000):
    server_address = ('', port) # Mudado para '' para aceitar conexões externas/proxy
    httpd = server_class(server_address, handler_class)
    print(f"Servidor API rodando em http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()