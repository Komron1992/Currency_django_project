import os
from dotenv import load_dotenv

# Указываем путь до .env.local, относительно текущей директории
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.local'))

# Пример вывода для проверки переменных
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
