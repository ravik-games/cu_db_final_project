import pandas as pd
import random
import os
from faker import Faker
from datetime import timedelta, date

def translit(text):
    symbols = str.maketrans(
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
        "abvgdeezzijklmnoprstufhzcss_y_eua"
    )
    return text.lower().translate(symbols)

used_emails = set() # Здесь будем хранить все выданные почты

# Инициализация Faker
fake = Faker('ru_RU')
Faker.seed(42)
random.seed(42)

# Настройки генерации
NUM_EMPLOYEES = 10_000

print("Начинаем генерацию масштабных HR-данных...")

# --- 1. DEPARTMENTS ---
departments_data = [
    (1, 'Департамент продаж', 'Москва, БЦ Омега, 5 этаж'),
    (2, 'IT: Разработка', 'Санкт-Петербург, БЦ Технопарк'),
    (3, 'IT: Инфраструктура', 'Санкт-Петербург, БЦ Технопарк'),
    (4, 'IT: Тестирование (QA)', 'Санкт-Петербург, БЦ Технопарк'),
    (5, 'HR: Подбор персонала', 'Москва, БЦ Омега, 4 этаж'),
    (6, 'HR: Кадровое делопроизводство', 'Москва, БЦ Омега, 4 этаж'),
    (7, 'Финансовый департамент', 'Казань, Иннополис'),
    (8, 'Бухгалтерия', 'Казань, Иннополис'),
    (9, 'Маркетинг и PR', 'Москва, БЦ Омега, 6 этаж'),
    (10, 'Служба безопасности', 'Москва, БЦ Омега, 1 этаж'),
    (11, 'Юридический отдел', 'Москва, БЦ Омега, 6 этаж'),
    (12, 'Служба поддержки клиентов', 'Екатеринбург, БЦ Высоцкий'),
    (13, 'Отдел логистики', 'Новосибирск, Складской комплекс А'),
    (14, 'Аналитика и Data Science', 'Санкт-Петербург, БЦ Технопарк'),
    (15, 'Административный отдел', 'Москва, БЦ Омега, 1 этаж')
]
df_departments = pd.DataFrame(departments_data, columns=['department_id', 'department_name', 'location'])

# Конфигурация отделов: (Вес_размера, Множитель_ЗП)
# Сделает одни отделы огромными с низкими зп, а другие — маленькими и элитными
dept_config = {
    1:  (20, 1.1),  # Продажи (крупный)
    2:  (12, 1.6),  # IT Разработка (средний, высокая ЗП)
    3:  (8,  1.4),  # IT Инфраструктура
    4:  (8,  1.2),  # QA
    5:  (4,  1.0),  # HR Подбор
    6:  (3,  0.9),  # HR Кадры (маленький)
    7:  (4,  1.4),  # Финансы
    8:  (3,  1.0),  # Бухгалтерия
    9:  (10, 1.1),  # Маркетинг
    10: (3,  0.9),  # СБ
    11: (3,  1.3),  # Юристы
    12: (35, 0.6),  # Поддержка (очень крупный, низкая ЗП)
    13: (12, 0.8),  # Логистика
    14: (5,  1.9),  # Data Science (маленький, очень высокая ЗП)
    15: (4,  0.8)   # Адм. отдел
}
dept_ids = list(dept_config.keys())
dept_weights = [v[0] for v in dept_config.values()]

# --- 2. POSITIONS ---
positions_data = [
    (1, 'Менеджер по продажам (Junior)'), (2, 'Менеджер по продажам (Middle)'), (3, 'Руководитель отдела продаж'),
    (4, 'Frontend Разработчик'), (5, 'Senior Backend Разработчик (Python)'), (6, 'Lead Java Developer'),
    (7, 'Системный администратор'), (8, 'DevOps Инженер'), (9, 'Специалист по информационной безопасности'),
    (10, 'QA Automation Engineer'), (11, 'Manual QA Engineer'),
    (12, 'IT Директор (CIO)'), (13, 'Продакт-менеджер'), (14, 'Проджект-менеджер'),
    (15, 'Рекрутер'), (16, 'HR Бизнес-партнер (HRBP)'), (17, 'Специалист по компенсациям и льготам'),
    (18, 'Бухгалтер по расчету ЗП'), (19, 'Главный бухгалтер'), (20, 'Финансовый аналитик'),
    (21, 'Data Scientist'), (22, 'BI Аналитик'), (23, 'Data Engineer'),
    (24, 'Специалист по контекстной рекламе'), (25, 'PR Менеджер'), (26, 'Директор по маркетингу (CMO)'),
    (27, 'Юрисконсульт'), (28, 'Старший юрист'),
    (29, 'Специалист службы поддержки'), (30, 'Руководитель смены (Support)'),
    (31, 'Логист'), (32, 'Офис-менеджер'), (33, 'Секретарь')
]
df_positions = pd.DataFrame(positions_data, columns=['position_id', 'position_name'])

# --- 3. EMPLOYEES ---
employees = []
employee_perf_tiers = {}  # Скрытый рейтинг для связи ЗП и оценок
employee_dept_mult = {}   # Запоминаем множитель отдела для генерации ЗП

for i in range(1, NUM_EMPLOYEES + 1):
    gender = random.choice(['M', 'F'])
    first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
    last_name = fake.last_name_male() if gender == 'M' else fake.last_name_female()

    base_name = f"{translit(first_name)}.{translit(last_name)}"
    email = f"{base_name}@company.com"

    while email in used_emails:
        random_suffix = random.randint(10, 99)
        email = f"{base_name}{random_suffix}@company.com"

    used_emails.add(email)

    display_email = email
    if random.random() < 0.015:
        display_email = display_email.replace('@', '')

    # Выбираем отдел на основе весов (Неравномерное распределение)
    department_id = random.choices(dept_ids, weights=dept_weights)[0]

    # Вариативность стажа в зависимости от отдела (в поддержке/продажах текучка выше)
    if department_id in [1, 12, 13]:
        hire_date = fake.date_between(start_date='-4y', end_date='today')
        is_active = random.random() > 0.40  # Высокая текучка
    else:
        hire_date = fake.date_between(start_date='-12y', end_date='today')
        is_active = random.random() > 0.15  # Стабильные отделы

    if not is_active:
        # Высокая вариативность: кто-то ушел через месяц, кто-то работал годами
        termination_date = hire_date + timedelta(days=random.randint(30, 2500))
        if termination_date > date.today():
            termination_date = date.today()
    else:
        termination_date = date(9999, 12, 31)

    # Присваиваем сотруднику скрытый "тир" успешности (от 1 до 5)
    perf_tier = random.choices([1, 2, 3, 4, 5], weights=[8, 17, 50, 18, 7])[0]
    employee_perf_tiers[i] = perf_tier
    employee_dept_mult[i] = dept_config[department_id][1]

    # Исправлено: пишем в базу display_email, чтобы битые почты реально доходили до CSV
    employees.append([i, first_name, last_name, display_email, is_active, hire_date, termination_date, department_id])

df_employees = pd.DataFrame(employees, columns=['employee_id', 'first_name', 'last_name', 'email', 'is_active', 'hire_date', 'termination_date', 'department_id'])

# --- 4. EMPLOYEE_POSITION ---
emp_positions = []
for emp_id in df_employees['employee_id']:
    pos_id = random.choice(df_positions['position_id'].tolist())
    emp_positions.append([pos_id, emp_id])
df_emp_position = pd.DataFrame(emp_positions, columns=['position_id', 'employee_id'])

# --- 5. SALARIES ---
salaries = []
outlier_counter = 0  # Счётчик для жесткого ограничения количества выбросов

for idx, row in df_employees.iterrows():
    emp_id = row['employee_id']
    hire_date = row['hire_date']
    term_date = row['termination_date']

    perf_tier = employee_perf_tiers[emp_id]
    dept_mult = employee_dept_mult[emp_id]

    num_salary_changes = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
    current_start = hire_date

    # Базовая ставка зависит от отдела и успешности (тиры 4 и 5 изначально получают чуть больше)
    tier_bonus = 1.0 + (perf_tier - 3) * 0.1
    base_salary = int(random.randint(70000, 180000) * dept_mult * tier_bonus)

    for i in range(num_salary_changes):
        is_last = (i == num_salary_changes - 1)
        amount = base_salary

        # Генерируем ОЧЕНЬ редкие и КРУПНЫЕ выбросы строго вверх (буквально 3-4 штуки на всю базу)
        if outlier_counter < 6 and random.random() < 0.0002:
            amount = int(base_salary * random.uniform(8.0, 50.0))
            outlier_counter += 1

        if is_last:
            valid_to = term_date
            is_valid = row['is_active']
        else:
            valid_to = current_start + timedelta(days=random.randint(180, 365))
            if valid_to > date.today(): valid_to = date.today()
            is_valid = False

        salaries.append([emp_id, amount, is_valid, current_start, valid_to])

        if not is_last:
            current_start = valid_to + timedelta(days=1)

        # Корреляция: Скорость роста ЗП напрямую завязана на перформанс-тир сотрудника
        if perf_tier == 5:
            growth = random.uniform(1.20, 1.40)  # Бурный рост у лучших
        elif perf_tier == 4:
            growth = random.uniform(1.10, 1.25)
        elif perf_tier == 3:
            growth = random.uniform(1.05, 1.12)
        else:
            growth = random.uniform(1.00, 1.04)  # Слабые сотрудники почти не растут в доходах

        base_salary = int(base_salary * growth)

df_salaries = pd.DataFrame(salaries, columns=['employee_id', 'amount', 'is_valid', 'valid_from', 'valid_to'])
df_salaries.insert(0, 'salary_id', range(1, 1 + len(df_salaries)))

# --- 6. PERFORMANCE REVIEWS ---
reviews = []

good_comments = [
    "Сотрудник стабильно перевыполняет KPI.", "Высокая степень самостоятельности при принятии решений.",
    "Отличные лидерские качества, успешно менторит стажеров.", "Блестяще реализовал ключевой проект в этом квартале.",
    "Проактивный подход к работе, всегда предлагает улучшения.", "Надежный член команды, соблюдает все сроки (SLA).",
    "Демонстрирует высокий уровень экспертности в предметной области.", "Отлично справляется с задачами в условиях высокой неопределенности.",
    "Клиенты высоко оценивают работу данного сотрудника.", "Внес значительный вклад в оптимизацию внутренних процессов."
]
bad_comments = [
    "Сотрудник регулярно нарушает сроки выполнения задач.", "Требуется усилить внимание к деталям, частые ошибки в отчетах.",
    "Низкая вовлеченность в командные процессы и митинги.", "Необходимо улучшить навыки коммуникации со смежными отделами.",
    "Показатели эффективности ниже ожидаемого уровня для данной должности.", "Игнорирует регламенты компании и требования безопасности.",
    "Поступает много жалоб со стороны внутренних заказчиков.", "Отсутствует инициатива, работает строго 'от звонка до звонка'.",
    "Конфликтен в общении с коллегами.", "Не справился с адаптацией к новым инструментам работы."
]
neutral_comments = [
    "Стабильный результат работы, компетенции соответствуют занимаемой должности.",
    "Рабочий процесс идет в штатном режиме, без существенных отклонений.",
    "Задачи выполняются в срок, ожидаемый уровень качества."
]

for idx, row in df_employees.iterrows():
    emp_id = row['employee_id']
    hire_date = row['hire_date']
    term_date = row['termination_date'] if not row['is_active'] else date.today()

    perf_tier = employee_perf_tiers[emp_id]
    years_worked = (term_date - hire_date).days // 365

    for y in range(max(1, years_worked)):
        review_date = hire_date + timedelta(days=(y * 365) + random.randint(15, 60))
        if review_date > date.today(): continue

        # Распределение оценок жестко зависит от скрытого тира (Обеспечивает корреляцию с ЗП)
        if perf_tier == 5:
            score_weights = [0, 0, 5, 35, 60]    # В основном 4 и 5
        elif perf_tier == 4:
            score_weights = [0, 5, 20, 60, 15]   # В основном 4
        elif perf_tier == 3:
            score_weights = [5, 15, 65, 12, 3]   # В основном стабильные 3
        elif perf_tier == 2:
            score_weights = [25, 55, 18, 2, 0]   # Тройки и двойки
        else:
            score_weights = [65, 25, 10, 0, 0]   # Хронические единицы и двойки

        score = random.choices([1, 2, 3, 4, 5], weights=score_weights)[0]

        if score in [4, 5]: comment = random.choice(good_comments)
        elif score == 3: comment = random.choice(neutral_comments)
        else: comment = random.choice(bad_comments)

        reviews.append([emp_id, review_date, score, comment])

df_reviews = pd.DataFrame(reviews, columns=['employee_id', 'review_date', 'score', 'comments'])
df_reviews.insert(0, 'review_id', range(1, 1 + len(df_reviews)))

# Создаем папку data, если ее не существует
os.makedirs('data', exist_ok=True)

df_departments.to_csv('data/departments.csv', index=False)
df_positions.to_csv('data/positions.csv', index=False)
df_employees.to_csv('data/employees.csv', index=False)
df_salaries.to_csv('data/salaries.csv', index=False)
df_reviews.to_csv('data/performance_reviews.csv', index=False)
df_emp_position.to_csv('data/employee_position.csv', index=False)

print(f"Готово! Сгенерировано:")
print(f"Сотрудников: {len(df_employees)}")
print(f"Изменений ЗП (SCD2): {len(df_salaries)}")
print(f"Оценок Performance: {len(df_reviews)}")
print(f"Искусственных супер-выбросов ЗП создано: {outlier_counter}")
