import pandas as pd
from sqlalchemy import create_engine, text

# 1. ТВОИ ДАННЫЕ ДЛЯ ПОДКЛЮЧЕНИЯ
DB_CONNECTION_STRING = 'postgresql://ravik:games@localhost:5432/hr_db'

# 2. Список файлов в правильном порядке (чтобы не нарушить связи Foreign Keys)
files_to_load = [
    ('departments', 'data/departments.csv'),
    ('positions', 'data/positions.csv'),
    ('employees', 'data/employees.csv'),
    ('salaries', 'data/salaries.csv'),
    ('performance_reviews', 'data/performance_reviews.csv'),
    ('employee_position', 'data/employee_position.csv')
]

def load_data():
    print("Подключение к базе данных...")
    engine = create_engine(DB_CONNECTION_STRING)

    # Открываем транзакцию
    with engine.begin() as conn:
        print("Очистка старых данных...")
        # TRUNCATE удалит все старые данные, чтобы не было дубликатов при повторных запусках
        conn.execute(text("TRUNCATE TABLE employee_position, performance_reviews, salaries, employees, positions, departments RESTART IDENTITY CASCADE;"))

        # Загружаем каждый файл
        for table_name, file_path in files_to_load:
            print(f"Загрузка {file_path} в таблицу {table_name}...")
            df = pd.read_csv(file_path)

            # Заливаем данные в БД (if_exists='append' добавляет строки к существующей таблице)
            df.to_sql(table_name, con=conn, if_exists='append', index=False)
            print(f"  Успешно загружено строк: {len(df)}")

    print("\nВся загрузка успешно завершена!")

if __name__ == "__main__":
    load_data()
