import json
import bcrypt
import jwt
import datetime

SECRET_KEY = "123456"  # Mantenha igual ao que está no Server.py

class Auth:
    def __init__(self, database):
        self.db = database

    # ---- CRIPTOGRAFAR SENHA (bcrypt) ----
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # ---- VERIFICAR SENHA (bcrypt) ----
    def verify_password(self, password, hashed):
        try:
            # Garante que sejam bytes
            if isinstance(password, str):
                password = password.encode("utf-8")
            if isinstance(hashed, str):
                hashed = hashed.encode("utf-8")
            
            # Tenta verificar. Se 'hashed' não for um hash válido, o bcrypt lança erro.
            return bcrypt.checkpw(password, hashed)
        except ValueError:
            # Se der erro de "Invalid Salt" (senha no banco não é hash), retorna False
            print("Aviso: A senha no banco de dados não está criptografada corretamente.")
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
                # Chama a verificação blindada
                if self.verify_password(senha, user["senha"]):
                    
                    tipo_usuario = user.get("tipo_usuario", "comum")
                    token = self.generate_token(user["id_user"], tipo_usuario)
                    
                    return 200, {
                        "message": "Login realizado com sucesso",
                        "token": token,
                        "user": {
                            "id": user["id_user"],
                            "email": user["email"],
                            "nome": user["nome"],
                            "tipo": tipo_usuario 
                        }
                    }
                else:
                    # Senha errada OU senha no banco corrompida (texto puro)
                    return 401, {"error": "Senha incorreta (ou banco desatualizado)"}

            return 404, {"error": "Email não encontrado"}

        except json.JSONDecodeError:
            return 400, {"error": "JSON inválido"}
        except Exception as e:
            print(f"Erro crítico no login: {e}") # Isso aparecerá no seu terminal Python
            return 500, {"error": f"Erro interno: {str(e)}"}

    # ---- GERAR TOKEN JWT ----
    def generate_token(self, usuario_id, tipo):
        payload = {
            "id": usuario_id,
            "tipo": tipo,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
    # ---- VERIFICAR TOKEN JWT ----
    def verify_token(self, token):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return None

    # ---- LOGIN (CORRIGIDO) ----
    def handle_login(self, body):
        try:
            data = json.loads(body)
            email = data.get("email")
            senha = data.get("senha")

            if not email or not senha:
                return 400, {"error": "Email e senha são obrigatórios"}

            # 🟢 MUDANÇA PRINCIPAL: 
            # Busca apenas na tabela de usuários (que agora contém admins e comuns)
            # Não usamos mais 'get_admin_by_email' pois ela foi removida.
            user = self.db.get_user_by_email(email)

            if user:
                # Verifica a senha
                if self.verify_password(senha, user["senha"]):
                    
                    # Pega o tipo do banco (admin ou comum)
                    tipo_usuario = user.get("tipo_usuario", "comum")
                    
                    # Gera o token com o ID e o TIPO corretos
                    token = self.generate_token(user["id_user"], tipo_usuario)
                    
                    return 200, {
                        "message": "Login realizado com sucesso",
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
            return 500, {"error": f"Erro interno: {str(e)}"}

    # ---- CADASTRO ----
    def handle_register(self, body):
        try:
            data = json.loads(body)
            nome = data.get("nome")
            email = data.get("email")
            senha = data.get("password") 

            if not nome or not email or not senha:
                return 400, {"error": "Nome, email e senha são obrigatórios"}

            if self.db.get_user_by_email(email):
                return 409, {"error": "Email já cadastrado"}

            senha_hash = self.hash_password(senha)

            # Cria usuário sempre como 'comum' por padrão
            sucesso = self.db.create_user(nome, email, senha_hash)

            if sucesso:
                return 201, {"message": "Usuário criado com sucesso!"}
            else:
                return 500, {"error": "Erro ao criar usuário"}

        except json.JSONDecodeError:
            return 400, {"error": "JSON inválido"}
        except Exception as e:
            return 500, {"error": f"Erro interno: {str(e)}"}

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
            
            sucesso = self.db.update_user(user_id, nome, email, senha_hash)

            if sucesso:
                return 200, {"status": "success", "message": "Perfil atualizado"}
            else:
                return 400, {"status": "error", "message": "Erro ao atualizar"}
        except Exception as e:
            return 500, {"status": "error", "message": str(e)}

    # ---- FILMES (Criação, Edição, Deleção) ----
    def handle_movie_creation(self, body, user_id):
        try:
            data = json.loads(body)
            movie_id = self.db.create_movie_complete(data, user_id, is_admin=False)
            if movie_id:
                return 201, {"status": "success", "message": "Filme enviado!", "id": movie_id}
            return 500, {"status": "error", "message": "Erro ao salvar"}
        except Exception as e:
            return 500, {"status": "error", "message": str(e)}

    def handle_movie_update(self, movie_id, body, payload):
        try:
            data = json.loads(body)
            # Aqui você pode usar update_movie_base ou criar um update_movie_complete no Database
            sucesso = self.db.update_movie_base(movie_id, data)
            if sucesso:
                return 200, {"status": "success", "message": "Editado com sucesso"}
            return 400, {"status": "error", "message": "Erro ao editar"}
        except Exception as e:
            return 500, {"status": "error", "message": str(e)}

    def handle_movie_deletion(self, movie_id, payload):
        if self.db.delete_movie(movie_id):
            return 200, {"status": "success", "message": "Deletado"}
        return 400, {"status": "error", "message": "Erro ao deletar"}