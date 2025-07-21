import psycopg2
from psycopg2 import OperationalError

def test_connection():
    connection = None  # Инициализируем переменную connection
    try:
        connection = psycopg2.connect(
            dbname="currency_db",
            user="currency_user",
            password="currency_pass",
            host="localhost",  # Или 'db' если через Docker
            port="5432"
        )
        print("✅ Подключение к БД успешно")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()

test_connection()
