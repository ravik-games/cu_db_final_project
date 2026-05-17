-- Создание таблиц
CREATE TABLE departments
(
    department_id SERIAL PRIMARY KEY,
    department_name TEXT NOT NULL,
    location TEXT NOT NULL
);

CREATE TABLE positions
(
    position_id SERIAL PRIMARY KEY,
    position_name TEXT NOT NULL UNIQUE
);

CREATE TABLE employees
(
    employee_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    hire_date DATE NOT NULL DEFAULT current_date,
    termination_date DATE NOT NULL DEFAULT '9999-12-31',
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE salaries -- Эта таблица использует SCD2
(
    salary_id SERIAL,
    employee_id INT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    is_valid BOOLEAN NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL DEFAULT '9999-12-31',
    PRIMARY KEY (salary_id, employee_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE performance_reviews
(
    review_id SERIAL,
    employee_id INT NOT NULL,
    review_date DATE NOT NULL,
    score INT NOT NULL CHECK (score >= 1 AND score <= 5),
    comments TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    PRIMARY KEY (review_id, employee_id)
);

CREATE TABLE employee_position
(
    position_id INT NOT NULL,
    employee_id INT NOT NULL,
    PRIMARY KEY (position_id, employee_id),
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- Тут загрузка скриптом

-- Демонстрация
SELECT *
FROM employees
LIMIT 100;

SELECT *
FROM departments;

SELECT *
FROM positions;

SELECT *
FROM salaries
LIMIT 100;

SELECT *
FROM employee_position
LIMIT 100;

SELECT *
FROM performance_reviews
LIMIT 100;

SELECT count(*) AS total_rows
FROM departments;

SELECT count(*) AS total_rows
FROM positions;

SELECT count(*) AS total_rows
FROM employees;

SELECT count(*) AS total_rows
FROM salaries;

SELECT count(*) AS total_rows
FROM performance_reviews;

SELECT count(*) AS total_rows
FROM employee_position;






-- Таблица для логирования ошибок валидации
CREATE TABLE IF NOT EXISTS validation_errors (
    error_id SERIAL PRIMARY KEY,
    table_name TEXT,
    record_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Валидация employee
CREATE OR REPLACE FUNCTION check_employee()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.email !~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' THEN -- Шаблон для regex взял из интернета
        INSERT INTO validation_errors (table_name, record_data, error_message)
        VALUES ('employees', to_jsonb(NEW), 'Неправильный формат почты: ' || NEW.email);
        RETURN NULL;
    END IF;
    IF NEW.first_name IS NULL OR NEW.first_name !~ '^[a-zA-Zа-яА-ЯёЁ]+([ ''-][a-zA-Zа-яА-ЯёЁ]+)*$' THEN -- Тут тоже
        INSERT INTO validation_errors (table_name, record_data, error_message)
        VALUES ('employees', to_jsonb(NEW), 'Неправильный формат имени: ' || NEW.first_name);
        RETURN NULL;
    END IF;
    IF NEW.last_name IS NULL OR NEW.last_name !~ '^[a-zA-Zа-яА-ЯёЁ]+([ ''-][a-zA-Zа-яА-ЯёЁ]+)*$' THEN -- Тут тоже
        INSERT INTO validation_errors (table_name, record_data, error_message)
        VALUES ('employees', to_jsonb(NEW), 'Неправильный формат фамилии: ' || NEW.last_name);
        RETURN NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS validate_employee ON employees;
CREATE TRIGGER validate_employee
    BEFORE INSERT OR UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION check_employee();

-- Примеры
DELETE FROM employees WHERE employee_id in (27011826, 737373, 373737);

INSERT INTO employees (employee_id, first_name, last_name, email, department_id, is_active)
VALUES (27011826, 'Михаил', 'Салтыков-Щедрин', 'pro.pisatel@empire.ru', 9, true);
SELECT * FROM employees WHERE email = 'pro.pisatel@empire.ru';

INSERT INTO employees (employee_id, first_name, last_name, email, department_id, is_active)
VALUES (737373, 'Иван', 'Иванов', 'test', 9, true);

INSERT INTO employees (employee_id, first_name, last_name, email, department_id, is_active)
VALUES (373737, 'Pro', 'Xx_H4ck3R_xX', 'hacker@test.com', 9, true);

SELECT *
FROM employees
WHERE employee_id in (27011826, 737373, 373737);

SELECT *
FROM validation_errors;






-- Загрузка данных SCD2
CREATE OR REPLACE PROCEDURE load_salaries_scd2()
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE salaries s
    SET
        valid_to = t.valid_from - INTERVAL '1 day',
        is_valid = false
    FROM temp_salaries_load t
    WHERE s.employee_id = t.employee_id
      AND s.is_valid = true
      AND s.amount <> t.amount;

    -- Открытие новых версий
    INSERT INTO salaries (employee_id, amount, is_valid, valid_from, valid_to)
    SELECT
        t.employee_id,
        t.amount,
        true,
        t.valid_from,
        '9999-12-31'::DATE
    FROM temp_salaries_load t
    WHERE NOT exists (
        SELECT 1
        FROM salaries s
        WHERE s.employee_id = t.employee_id
          AND s.is_valid = true
          AND s.amount = t.amount
    );

    TRUNCATE TABLE temp_salaries_load;
END;
$$;

-- Примеры
DROP TABLE IF EXISTS temp_salaries_load;
CREATE TEMP TABLE IF NOT EXISTS temp_salaries_load (
    employee_id INT,
    amount INT,
    valid_from DATE
);

DELETE FROM salaries WHERE employee_id in (27011826, 737373, 373737);
DELETE FROM employees WHERE employee_id in (27011826, 737373, 373737);
INSERT INTO employees (employee_id, first_name, last_name, email, department_id)
VALUES (27011826, 'Михаил', 'Салтыков-Щедрин', 'pro.pisatel@empire.ru', 9),
       (373737, 'Тест', 'Тестов', 'test@test.test', 3);
INSERT INTO salaries (employee_id, amount, is_valid, valid_from, valid_to)
VALUES (27011826, 100000, true, '2023-01-01', '9999-12-31');

INSERT INTO temp_salaries_load (employee_id, amount, valid_from)
VALUES (27011826, 200000, current_date),
       (373737, 125000, current_date);

CALL load_salaries_scd2();

SELECT *
FROM salaries
WHERE employee_id in (27011826, 737373, 373737)
ORDER BY employee_id, valid_from;






-- Аналитический запрос
-- Чтобы потом в оптимизациях удобнее пользоваться, оберну в представление
DROP VIEW IF EXISTS analytical_query;
CREATE OR REPLACE VIEW analytical_query AS
WITH active_salaries AS (
    SELECT
        employee_id,
        amount
    FROM salaries
    WHERE is_valid = TRUE
),
    employee_avg_performance AS (
    SELECT
        employee_id,
        AVG(score) AS avg_score
    FROM performance_reviews
    GROUP BY employee_id
)
SELECT
    d.department_name,
    count(e.employee_id) AS total_employees,
    sum(CASE WHEN e.is_active = FALSE THEN 1 ELSE 0 END) AS terminated_employees,
    round(avg(CASE WHEN e.is_active = FALSE THEN e.termination_date - e.hire_date END), 0) AS avg_days_before_exit,
    round(avg(s.amount), 0) AS avg_salary,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY s.amount) AS median_salary, -- Уточнял на семинаре, сказали что такую конструкцию можно
    max(s.amount) - min(s.amount) AS salary_spread,
    round(corr(s.amount, pr.avg_score)::NUMERIC, 2) AS salary_performance_corr
FROM departments d
    JOIN employees e ON d.department_id = e.department_id
    LEFT JOIN active_salaries s ON e.employee_id = s.employee_id
    LEFT JOIN employee_avg_performance pr ON e.employee_id = pr.employee_id
GROUP BY d.department_id, d.department_name;
SELECT * FROM analytical_query;



-- Оптимизации
DROP INDEX IF EXISTS idx_salaries_active_amount, idx_performance_reviews_score;

EXPLAIN ANALYZE
SELECT * FROM analytical_query;

CREATE INDEX idx_salaries_active_amount ON salaries (employee_id, amount) WHERE is_valid = TRUE;
CREATE INDEX idx_performance_reviews_score ON performance_reviews (employee_id, score);

EXPLAIN ANALYZE
SELECT * FROM analytical_query;
-- У меня стало примерно на 5 мс быстрее (было 25, стало 20), индексы задействуются там, где надо
-- Не использовал партиции, так как данных мало и они скорее помешают, чем помогут