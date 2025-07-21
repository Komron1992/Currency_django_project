# fix_database_data.py
# Запустите этот скрипт для исправления данных в базе

import os
import django
from django.db import connection
from django.utils import timezone

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()


def fix_datetime_fields():
    """Исправляет некорректные значения datetime в базе данных"""

    with connection.cursor() as cursor:
        # Список таблиц и полей для исправления
        tables_to_fix = [
            ('app_currencyexchangerate', 'created_at'),
            ('app_marketexchangerate', 'created_at'),
            ('app_workeractivity', 'created_at'),
        ]

        current_time = timezone.now().isoformat()

        for table, field in tables_to_fix:
            try:
                # Проверяем существование таблицы
                cursor.execute(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{table}';
                """)
                if not cursor.fetchone():
                    print(f"Таблица {table} не существует, пропускаем...")
                    continue

                # Проверяем существование поля
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                if field not in columns:
                    print(f"Поле {field} не существует в таблице {table}, пропускаем...")
                    continue

                # Ищем некорректные значения
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table} 
                    WHERE {field} IS NOT NULL 
                    AND typeof({field}) != 'text'
                """)
                count = cursor.fetchone()[0]

                if count > 0:
                    print(f"Найдено {count} некорректных записей в {table}.{field}")

                    # Исправляем некорректные значения
                    cursor.execute(f"""
                        UPDATE {table} 
                        SET {field} = ? 
                        WHERE {field} IS NOT NULL 
                        AND typeof({field}) != 'text'
                    """, [current_time])

                    print(f"Исправлено {count} записей в {table}.{field}")
                else:
                    print(f"Некорректных записей в {table}.{field} не найдено")

            except Exception as e:
                print(f"Ошибка при обработке {table}.{field}: {e}")


if __name__ == "__main__":
    print("Начинаем исправление данных...")
    fix_datetime_fields()
    print("Готово!")