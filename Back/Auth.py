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
