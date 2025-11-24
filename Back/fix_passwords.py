import mysql.connector
import bcrypt

def fix_passwords():
    print("Iniciando correção de senhas...")
    
    try:
        # 1. Conectar ao banco de dados
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root", # Confirme se sua senha do banco é 'root'
            database="filmes"
        )
        cursor = mydb.cursor()

        # 2. Definir a senha padrão e gerar o hash seguro
        senha_padrao = "1234"
        # Gera o hash bcrypt (ex: $2b$12$........)
        hashed = bcrypt.hashpw(senha_padrao.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        print(f"Hash seguro gerado para a senha '{senha_padrao}': {hashed}")

        # 3. Atualizar Usuário Comum (Rebeca)
        # Garante que ela tenha a senha certa e seja do tipo 'comum'
        cursor.execute("UPDATE usuarios SET senha = %s, tipo_usuario = 'comum' WHERE email = 'Rebs@gmail.com'", (hashed,))
        print(f"Usuário 'Rebs@gmail.com' atualizado. (Linhas afetadas: {cursor.rowcount})")

        # 4. Atualizar Administrador
        # Garante que ele tenha a senha certa e seja do tipo 'admin'
        cursor.execute("UPDATE usuarios SET senha = %s, tipo_usuario = 'admin' WHERE email = 'administrador@ADM.com'", (hashed,))
        print(f"Usuário 'administrador@ADM.com' atualizado para Admin. (Linhas afetadas: {cursor.rowcount})")

        # 5. Confirmar as mudanças no banco
        mydb.commit()
        print("\n✅ SUCESSO! As senhas foram corrigidas.")
        print("Agora você pode fazer login com a senha '1234'.")

    except mysql.connector.Error as err:
        print(f"❌ Erro de Banco de Dados: {err}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'mydb' in locals(): mydb.close()

if __name__ == "__main__":
    fix_passwords()