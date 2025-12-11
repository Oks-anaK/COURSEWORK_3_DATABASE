from typing import Any, List, Optional, Tuple

import psycopg2


class DBManager:
    """Класс, который будет подключаться к БД PostgreSQL и иметь следующие методы:
    get_companies_and_vacancies_count()
     — получает список всех компаний и количество вакансий у каждой компании.
    get_all_vacancies()
     — получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.
    get_avg_salary()
     — получает среднюю зарплату по вакансиям.
    get_vacancies_with_higher_salary()
     — получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
    get_vacancies_with_keyword()
     — получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python.
    """

    __slots__ = ["params", "conn"]

    def __init__(
        self, host: str, database: str, user: str, password: str, port: int = 5432
    ) -> None:
        """Функция инициализации атрибутов."""
        self.params = {
            "host": host,
            "dbname": database,
            "user": user,
            "password": password,
            "port": port,
        }
        self.conn = psycopg2.connect(**self.params)

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT e.name_employer, COUNT(*) as vacancies_count
            FROM employers e
            JOIN vacancies v ON e.id_employer = v.id_employer
            GROUP BY e.id_employer, e.name_employer
            ORDER BY vacancies_count DESC;
            """
            )
            return cursor.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[float], str]]:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT e.name_employer, v.vacancy_title, v.vacancy_salary,
                   v.vacancy_url
            FROM vacancies v
            JOIN employers e ON v.id_employer = e.id_employer;
            """
            )
            return cursor.fetchall()

    def get_avg_salary(self) -> List[Tuple[Optional[float]]]:
        """Получает среднюю зарплату по вакансиям."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT AVG(vacancy_salary) AS avg_salary
            FROM vacancies
            WHERE vacancy_salary <> 0;
            """
            )
            return cursor.fetchall()

    def get_vacancies_with_higher_salary(
        self,
    ) -> List[Tuple[str, int, Optional[float], str, str]]:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        Возвращает только уникальные вакансии по названию (оставляет вакансию с максимальной зарплатой).
        Названия нормализуются (убираются лишние пробелы) для корректного сравнения."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT DISTINCT ON (TRIM(vacancy_title))
                vacancy_title, id_employer, vacancy_salary, vacancy_description, vacancy_url
            FROM vacancies v
            WHERE vacancy_salary > (SELECT AVG(vacancy_salary) FROM vacancies WHERE vacancy_salary <> 0)
            ORDER BY TRIM(vacancy_title), vacancy_salary DESC;
            """
            )
            return cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[Any, ...]]:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
            SELECT * FROM vacancies
            WHERE vacancy_title ILIKE %s
            """,
                (f"%{keyword}%",),
            )  # ILIKE для регистронезависимого поиска
            return cursor.fetchall()

    def close(self) -> None:
        """Закрывает соединение с БД."""
        if self.conn and not self.conn.closed:
            self.conn.close()
