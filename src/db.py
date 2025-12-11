import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database(database_name: str, params: dict):
    """Пересоздаёт базу данных, завершая все активные сеансы."""
    # Подключаемся к postgres БД
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    try:
        # Принудительно завершаем все сеансы с этой БД
        cur.execute(
            f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database_name}'
            AND pid <> pg_backend_pid();
        """
        )

        # Удаляем БД, если она существует
        cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
        print(f"Старая база данных {database_name} удалена")

        # Небольшая пауза для завершения процессов
        import time

        time.sleep(0.5)

        # Создаём новую БД
        cur.execute(f"CREATE DATABASE {database_name}")
        print(f"База данных {database_name} успешно создана")

    except psycopg2.errors.DuplicateDatabase:
        print(f"База данных {database_name} уже существует")
    except Exception as e:
        print(f"Ошибка при работе с БД: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Подключение к текущей базе данных
    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE employers (
                id_employer SERIAL PRIMARY KEY,
                name_employer VARCHAR NOT NULL,
                employer_vacancies_url TEXT,
                employer_description TEXT,
                open_vacancies INTEGER,
                employer_url TEXT
            )
        """
        )

    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE vacancies (
                vacancy_title VARCHAR NOT NULL,
                id_employer INT REFERENCES employers(id_employer),
                vacancy_salary FLOAT,
                vacancy_description TEXT,
                vacancy_url TEXT
            )
        """
        )

    conn.commit()
    cur.close()


def save_data_to_database(
    data_employers: list[dict],
    data_vacancies: list[dict],
    database_name: str,
    params: dict,
):
    """Сохранение данных о вакансиях и работодателях в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer in data_employers:
            cur.execute(
                """
                INSERT INTO employers (
                    name_employer, employer_vacancies_url, employer_description,
                    open_vacancies, employer_url
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_employer
                """,
                (
                    employer.get("name_employer"),
                    employer.get("employer_vacancies_url"),
                    employer.get("employer_description"),
                    employer.get("open_vacancies"),
                    f'https://hh.ru/employer/{employer.get("id_employer")}',
                ),
            )
            id_employer = cur.fetchone()[0]
            # Получаем внешний ID работодателя для фильтрации
            employer_external_id = employer.get("id_employer")

            for vacancy in data_vacancies:
                # Проверяем, что вакансия принадлежит этому работодателю
                if vacancy.get("id_employer") == employer_external_id:
                    cur.execute(
                        """
                        INSERT INTO vacancies (
                            vacancy_title, id_employer, vacancy_salary,
                            vacancy_description, vacancy_url
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            vacancy.get("title"),
                            id_employer,
                            vacancy.get("salary"),
                            vacancy.get("description"),
                            f'https://hh.ru/vacancy/{vacancy.get("id_vacancy")}',
                        ),
                    )

        conn.commit()
        conn.close()
