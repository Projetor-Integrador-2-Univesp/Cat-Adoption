from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

# Usando variáveis separadas
host = os.getenv('SUPABASE_HOST')
port = os.getenv('SUPABASE_PORT')
name = os.getenv('SUPABASE_NAME')
user = os.getenv('SUPABASE_USER')
password = os.getenv('SUPABASE_PASSWORD')

print(f"Host: {host}")
print(f"User: {user}")
print(f"Password: {'*' * len(password) if password else 'N/A'}")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=name,
        user=user,
        password=password,
        sslmode='require'
    )
    print("✅ CONEXÃO BEM SUCEDIDA!")
    conn.close()
except Exception as e:
    print(f"❌ ERRO: {e}")