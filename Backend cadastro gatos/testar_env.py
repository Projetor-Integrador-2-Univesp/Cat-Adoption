from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
name = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

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
        sslmode="require"
    )

    print("Conexão bem-sucedida!")
    conn.close()

except Exception as e:
    print(f"ERRO: {e}")
