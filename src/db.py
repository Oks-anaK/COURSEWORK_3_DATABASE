import psycopg2

def create_database(database_name, params):
    """Создание базы данных и таблиц с работодателями и вакансиями."""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    try:

        cur.execute(f"DROP DATABASE {database_name}")

    except Exception as e:

        print(f'Информация: {e}')

    cur.execute(f'CREATE DATABASE {database_name}')

    cur.close()
    conn.close()

# Подключение к текущей базе данных
    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE employers (
                id_employer SERIAL PRIMARY KEY,
                name_employer VARCHAR NOT NULL,
                employer_vacancies_url TEXT,
                employer_description TEXT,
                open_vacancies INTEGER,
                employer_url TEXT
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_title VARCHAR NOT NULL,
                id_employer INT REFERENCES employers(id_employer),
                vacancy_salary FLOAT,
                vacancy_description TEXT,
                vacancy_url TEXT
            )
        """)

    conn.commit()
    cur.close()

def save_data_to_database(data_employers: list[dict], data_vacancies: list[dict], database_name: str, params: dict):
    """Сохранение данных о вакансиях и работодателях в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer in data_employers:
            cur.execute(
                """
                INSERT INTO employers (name_employer, employer_vacancies_url, employer_description, open_vacancies, employer_url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_employer
                """,
                (employer.get('name_employer'), employer.get('employer_vacancies_url'), employer.get('employer_description'),
                 employer.get('open_vacancies'), f'https://hh.ru/employer/{employer.get("id_employer")}')
            )
            id_employer = cur.fetchone()[0]
            for vacancy in data_vacancies:
                cur.execute(
                    """
                    INSERT INTO vacancies (vacancy_title, id_employer, vacancy_salary, vacancy_description, vacancy_url)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (vacancy.get('title'), id_employer, vacancy.get('salary'), vacancy.get('description'), f'https://hh.ru/vacancy/{vacancy.get('id_vacancy')}')
                )
    conn.commit()
    cur.close()
