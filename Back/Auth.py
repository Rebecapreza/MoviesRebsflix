import secrets # <-- Módulo importado para gerar tokens
import hashlib
import Database as db

# Dicionario para os tokens
sessions = {}
# Chave para embaralhar
SALT = b'your_project_salt_CINESTESIA'

def hash_password(password):
    """Gera o hash da senha usando PBKDF2."""
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        SALT, 
        100000
    )
    return pwd_hash.hex()

def verify_password(plain_password, password_from_db):
    """
    Compara o hash da senha fornecida com o hash armazenado no DB.
    (Adaptado do seu código original para usar a função de hash)
    """
    # 🚨 NOTA: Como você não usa o hash_password() no handle_register (apenas 'password'), 
    # eu mantenho a comparação de texto simples por enquanto, 
    # mas o ideal seria usar: return hash_password(plain_password) == password_from_db
    return plain_password == password_from_db 
    # Se você começar a armazenar o hash no DB, use: return hash_password(plain_password) == password_from_db

# Cadastro
def handle_register(nome, email, password):
    user = db.get_user_by_email(email)
    if user:
        return None 

    # O código original armazenava a senha em texto puro (password), manteremos assim, 
    # mas o ideal é usar: hashed_pass = hash_password(password)
    hashed_pass = password 

    tipo_usuario = 'Comum'
    
    # 🚨 CRÍTICO: db.create_user deve receber 4 parâmetros (nome, email, senha, tipo_usuario)
    new_user_id = db.create_user(nome, email, hashed_pass, tipo_usuario)
    return {'id_usuario': new_user_id, 'email': email}

# Login
def handle_login(email, password):
    user = db.get_user_by_email(email)

    # Verifica a senha usando a função de comparação
    if user and verify_password(password, user['senha']):
        # Gera o token
        token = secrets.token_hex(20)

        # Guarda os tokens dos usuarioos
        sessions[token] = {
            'id_usuario': user['id_usuario'],
            'nome': user['nome'],
            'tipo_usuario': user['tipo_usuario']
        }
        return {'token': token, 'user_type': user['tipo_usuario'], 'nome': user['nome']}
    else:
        return None

# Verificação do token
def get_user_from_token(auth_header):
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    user_data = sessions.get(token)
    return user_data

# Função para sair
def handle_logout(auth_header):
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    if token in sessions:
        del sessions[token]
        return True
    return False