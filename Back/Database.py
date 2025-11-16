import mysql.connector
from mysql.connector import errorcode
import json

class _DatabaseConnection:
    # Configurações do banco
    def __init__(self):
        self.config = {
            # 🚨 CRÍTICO: Ajuste essas credenciais se necessário
            'user': 'root',
            'password': 'root', 
            'host': 'localhost',
            'database': 'Filmes',
            'raise_on_warnings': True
        }
        try:
            self.mydb = mysql.connector.connect(**self.config)
            self.mydb.autocommit = True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erro de acesso: usuário ou senha do DB inválidos")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database não existe")
            else:
                print(err)
            exit(1)

    def fetch_all(self, query, params=None):
        cursor = self.mydb.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        return results

    def fetch_one(self, query, params=None):
        cursor = self.mydb.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        cursor.close()
        return result

    def execute_query(self, query, params=None):
        cursor = self.mydb.cursor()
        try:
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except mysql.connector.Error as err:
            cursor.close()
            # Adicionado print do erro para debug
            print(f"Erro na query: {err}") 
            return None

db_instance = _DatabaseConnection()

def get_or_create_id(table_name, name):
    """
    Função auxiliar para encontrar o ID de um nome em uma tabela (ator, diretor, produtora).
    Se não existir, cria um novo registro e retorna o novo ID.
    """
    if not name or not name.strip():
        return None

    # Mapeamento para nomes de colunas que podem variar
    id_col = f"id_{table_name}"
    name_col = "nome" if table_name not in ['genero', 'ator', 'diretor'] else table_name # Ajuste para 'genero'
    
    query_find = f"SELECT {id_col} FROM {table_name} WHERE {name_col} = %s"
    result = db_instance.fetch_one(query_find, (name,))
    
    if result:
        return result[id_col]
    
    query_create = f"INSERT INTO {table_name} ({name_col}) VALUES (%s)"
    new_id = db_instance.execute_query(query_create, (name,))
    return new_id


# --- Funções de Usuário ---

def get_user_by_email(email):
    # 🚨 NOTA: Assumindo que a tabela de usuários se chama 'usuario' (minúsculo)
    query = "SELECT * FROM usuario WHERE email = %s"
    return db_instance.fetch_one(query, (email,))

def create_user(nome, email, senha_hash, tipo_usuario):
    query = "INSERT INTO usuario (nome, email, senha, tipo_usuario) VALUES (%s, %s, %s, %s)"
    return db_instance.execute_query(query, (nome, email, senha_hash, tipo_usuario))


# --- Funções de Filme (CRUD e Busca) ---

def _map_filme_details(filme):
    """Função auxiliar para formatar a saída dos detalhes do filme."""
    if filme:
        # Divide as strings GROUP_CONCAT em listas (ou mantém None/vazio)
        filme['generos'] = [g.strip() for g in filme['generos'].split(',')] if filme['generos'] else []
        filme['atores'] = [a.strip() for a in filme['atores'].split(',')] if filme['atores'] else []
        filme['diretores'] = [d.strip() for d in filme['diretores'].split(',')] if filme['diretores'] else []
        
        # Para o front-end, o MovieForm espera uma string de gênero
        filme['genero_unico'] = filme['generos'][0] if filme['generos'] else ''

    return filme

def get_filme_by_id(filme_id):
    query = """
    SELECT 
        f.id_filme, f.titulo, f.ano, f.sinopse, f.poster, f.status_aprovacao, f.id_usuario,
        p.nome AS produtora_nome, p.id_produtora,
        GROUP_CONCAT(DISTINCT g.nome) AS generos,
        GROUP_CONCAT(DISTINCT a.nome) AS atores,
        GROUP_CONCAT(DISTINCT d.nome) AS diretores
    FROM filme f
    LEFT JOIN produtora p ON f.id_produtora = p.id_produtora
    LEFT JOIN filme_genero fg ON f.id_filme = fg.id_filme
    LEFT JOIN genero g ON fg.id_genero = g.id_genero
    LEFT JOIN filme_ator fa ON f.id_filme = fa.id_filme
    LEFT JOIN ator a ON fa.id_ator = a.id_ator
    LEFT JOIN filme_diretor fd ON f.id_filme = fd.id_filme
    LEFT JOIN diretor d ON fd.id_diretor = d.id_diretor
    WHERE f.id_filme = %s
    GROUP BY f.id_filme
    """
    filme = db_instance.fetch_one(query, (filme_id,))
    return _map_filme_details(filme)


def get_all_filmes(titulo=None, ano=None, genero=None):
    base_query = """
    SELECT f.id_filme, f.titulo, f.ano, f.poster, f.status_aprovacao, 
           GROUP_CONCAT(DISTINCT g.nome) AS generos
    FROM filme f
    LEFT JOIN filme_genero fg ON f.id_filme = fg.id_filme
    LEFT JOIN genero g ON fg.id_genero = g.id_genero
    """
    conditions = ["f.status_aprovacao = 'Aprovado'"]
    params = []

    if titulo:
        conditions.append("f.titulo LIKE %s")
        params.append(f"%{titulo}%")
    if ano:
        conditions.append("f.ano = %s")
        params.append(ano)
    if genero:
        # Se um gênero for especificado, precisamos filtrar por ele.
        # Uma forma simples é adicionar o JOIN novamente ou usar uma subconsulta, mas para simplicidade, 
        # faremos a filtragem no nível do GROUP_CONCAT ou exigimos que a query seja mais específica.
        # Adicionei a condição no WHERE para o filtro de gênero
        conditions.append("g.nome = %s")
        params.append(genero)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " GROUP BY f.id_filme"
    
    # 🚨 NOTA: Mapeamento básico para a lista (o front-end espera 'generos' como string para exibição na Home)
    raw_results = db_instance.fetch_all(base_query, params)
    
    # Formata a lista de filmes para o front-end
    formatted_results = []
    for row in raw_results:
        # Concatena a lista de gêneros em uma string simples para o MovieCard
        row['generos_str'] = ", ".join([g.strip() for g in row['generos'].split(',')]) if row['generos'] else ''
        formatted_results.append(row)
        
    return formatted_results


def get_pending_filmes():
    query = """
    SELECT id_filme, titulo, ano, status_aprovacao 
    FROM filme 
    WHERE status_aprovacao IN ('Pendente_Adicao', 'Pendente_Edicao')
    """
    return db_instance.fetch_all(query)


def create_filme(data, user_id):
    # A função get_or_create_id espera a tabela singular (produtora)
    produtora_id = get_or_create_id('produtora', data.get('produtora_nome'))
    
    query_filme = """
    INSERT INTO filme (titulo, ano, sinopse, poster, id_produtora, id_usuario, status_aprovacao) 
    VALUES (%s, %s, %s, %s, %s, %s, 'Pendente_Adicao')
    """
    filme_params = (
        data['titulo'], data['ano'], data['sinopse'], 
        data['poster'], produtora_id, user_id
    )
    filme_id = db_instance.execute_query(query_filme, filme_params)
    
    if not filme_id:
        return None

    # Insere Gêneros
    # Os dados esperam 'generos' como lista de IDs de gênero
    if 'generos' in data and data['generos']:
        for gen_id in data['generos']:
            db_instance.execute_query("INSERT INTO filme_genero (id_filme, id_genero) VALUES (%s, %s)", (filme_id, gen_id))
    
    # Insere Ator e Diretor (assumindo apenas um por enquanto)
    # A função get_or_create_id foi adaptada para criar se não existir.
    ator_id = get_or_create_id('ator', data.get('ator_nome'))
    diretor_id = get_or_create_id('diretor', data.get('diretor_nome'))
    
    if ator_id:
        db_instance.execute_query("INSERT INTO filme_ator (id_filme, id_ator) VALUES (%s, %s)", (filme_id, ator_id))
    if diretor_id:
        db_instance.execute_query("INSERT INTO filme_diretor (id_filme, id_diretor) VALUES (%s, %s)", (filme_id, diretor_id))
            
    return filme_id


def update_filme_admin(filme_id, data):
    # 🚨 NOTA: Atualiza para 'Aprovado'
    query = "UPDATE filme SET titulo = %s, ano = %s, sinopse = %s, poster = %s, status_aprovacao = 'Aprovado' WHERE id_filme = %s"
    params = (
        data['titulo'], data['ano'], data['sinopse'], 
        data['poster'], filme_id
    )
    return db_instance.execute_query(query, params)

def update_filme_comum(filme_id, data):
    # 🚨 NOTA: Atualiza para 'Pendente_Edicao'
    query = "UPDATE filme SET titulo = %s, ano = %s, sinopse = %s, poster = %s, status_aprovacao = 'Pendente_Edicao' WHERE id_filme = %s"
    params = (
        data['titulo'], data['ano'], data['sinopse'], 
        data['poster'], filme_id
    )
    return db_instance.execute_query(query, params)

def approve_filme(filme_id):
    query = "UPDATE filme SET status_aprovacao = 'Aprovado' WHERE id_filme = %s"
    return db_instance.execute_query(query, (filme_id,))

def delete_filme(filme_id):
    # Deletar em tabelas de relacionamento antes da tabela principal
    db_instance.execute_query("DELETE FROM filme_genero WHERE id_filme = %s", (filme_id,))
    db_instance.execute_query("DELETE FROM filme_ator WHERE id_filme = %s", (filme_id,))
    db_instance.execute_query("DELETE FROM filme_diretor WHERE id_filme = %s", (filme_id,))
    # Deletar filme
    return db_instance.execute_query("DELETE FROM filme WHERE id_filme = %s", (filme_id,))

def get_all_generos():
    query = "SELECT id_genero, nome FROM genero ORDER BY nome ASC"
    results = db_instance.fetch_all(query)
    return results

def get_all_anos():
    query = "SELECT DISTINCT ano FROM filme WHERE ano IS NOT NULL ORDER BY ano DESC"
    results = db_instance.fetch_all(query)
    return [row['ano'] for row in results]