import json
import bcrypt
import jwt
import datetime

SECRET_KEY = "123456"  # Chave secreta usada para gerar e validar o TOKEN JWT.

class Auth:
    def __init__(self, database):
        self.db = database

    # ---- CRIPTOGRAFAR SENHA (bcrypt) ----
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # ---- VERIFICAR SENHA (bcrypt) ----
    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

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
        # Tenta decodificar o token
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


    # ---- LOGIN ----
    def handle_login(self, body):
        try:
            data = json.loads(body)
            email = data.get("email")
            senha = data.get("senha")

            if not email or not senha:
                return 400, {"error": "Email e senha são obrigatórios"}

            # ---- LOGIN ADMIN ----
            admin = self.db.get_admin_by_email(email)
            if admin:
                if self.verify_password(senha, admin["senha"]):
                    token = self.generate_token(admin["id_adm"], "admin")
                    return 200, {
                        "message": "Login realizado com sucesso",
                        "tipo": "admin",
                        "id": admin["id_adm"],
                        "token": token
                    }
                return 401, {"error": "Senha incorreta"}

            # ---- LOGIN USUÁRIO ----
            user = self.db.get_user_by_email(email)
            if user:
                if self.verify_password(senha, user["senha"]):
                    token = self.generate_token(user["id_user"], "usuario")
                    return 200, {
                        "message": "Login realizado com sucesso",
                        "tipo": "usuario",
                        "id": user["id_user"],
                        "nome": user["nome"],
                        "token": token
                    }
                return 401, {"error": "Senha incorreta"}

            return 404, {"error": "Email não encontrado"}

        except json.JSONDecodeError:
            return 400, {"error": "JSON inválido"}
        except Exception as e:
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

            # Verifica se já existe usuário com o email
            if self.db.get_user_by_email(email):
                return 409, {"error": "Email já cadastrado"}

            # ---- CRIPTOGRAFAR SENHA ANTES DE SALVAR ----
            senha_hash = self.hash_password(senha)

            # Criar usuário
            sucesso = self.db.create_user(nome, email, senha_hash)

            if sucesso:
                return 201, {"message": "Usuário criado com sucesso!"}
            else:
                return 500, {"error": "Erro ao criar usuário"}

        except json.JSONDecodeError:
            return 400, {"error": "JSON inválido"}
        except Exception as e:
            return 500, {"error": f"Erro interno: {str(e)}"}
            
    # ---- ATUALIZAR PERFIL ----
    def handle_profile_update(self, body, payload):
        try:
            data = json.loads(body)
            user_id = payload["id"]
            user_type = payload["tipo"] 
            
            # O front-end (Profile.jsx) só envia essas 3 propriedades
            nome = data.get("nome")
            email = data.get("email")
            senha_nova = data.get("senha")
            
            if not user_id:
                return 401, {"status": "error", "message": "ID de usuário ausente no token."}
            
            # O front-end (Profile.jsx) usa '••••••••' se a senha não foi alterada
            senha_hash = None
            if senha_nova and senha_nova != "••••••••": 
                senha_hash = self.hash_password(senha_nova)
            
            sucesso = self.db.update_user(user_id, nome, email, senha_hash)

            if sucesso:
                return 200, {"status": "success", "message": "Perfil atualizado com sucesso"}
            else:
                return 400, {"status": "error", "message": "Nenhum dado para alterar ou erro no banco."}

        except json.JSONDecodeError:
            return 400, {"status": "error", "message": "JSON inválido"}
        except Exception as e:
            return 500, {"status": "error", "message": f"Erro interno: {str(e)}"}

    # ---- CRIAÇÃO DE FILME  ----
    def handle_movie_creation(self, body, user_id):
        try:
            data = json.loads(body)
            titulo = data.get("titulo")
            sinopse = data.get("sinopse")
            poster_url = data.get("poster_url")
            ano = data.get("ano")
            
            if not titulo or not sinopse or not poster_url or not ano:
                return 400, {"status": "error", "message": "Título, sinopse, poster e ano são obrigatórios."}
            
            movie_id = self.db.create_movie_base(titulo, sinopse, poster_url, ano, user_id)
            
            if movie_id:
                return 201, {"status": "success", "message": "Filme cadastrado com sucesso! (Pendente de aprovação)", "id_filme": movie_id}
            else:
                return 500, {"status": "error", "message": "Erro ao salvar filme no banco de dados."}

        except json.JSONDecodeError:
            return 400, {"status": "error", "message": "JSON inválido"}
        except Exception as e:
            return 500, {"status": "error", "message": f"Erro interno na criação do filme: {str(e)}"}

    # ---- ATUALIZAÇÃO DE FILME ----
    def handle_movie_update(self, movie_id, body, payload):
        try:
            data = json.loads(body)
            
            if not movie_id:
                 return 400, {"status": "error", "message": "ID do filme é obrigatório."}

            sucesso = self.db.update_movie_base(movie_id, data)
            
            if sucesso:
                return 200, {"status": "success", "message": "Filme editado com sucesso!"}
            else:
                return 404, {"status": "error", "message": "Filme não encontrado ou nenhum dado para alterar."}

        except json.JSONDecodeError:
            return 400, {"status": "error", "message": "JSON inválido"}
        except Exception as e:
            return 500, {"status": "error", "message": f"Erro interno na edição do filme: {str(e)}"}
            
    # ---- DELEÇÃO DE FILME  ----
    def handle_movie_deletion(self, movie_id, payload):
        try:
            if not movie_id:
                 return 400, {"status": "error", "message": "ID do filme é obrigatório."}

            sucesso = self.db.delete_movie(movie_id)
            
            if sucesso:
                return 200, {"status": "success", "message": "Filme excluído com sucesso!"}
            else:
                return 404, {"status": "error", "message": "Filme não encontrado."}

        except Exception as e:
            return 500, {"status": "error", "message": f"Erro interno na exclusão do filme: {str(e)}"}