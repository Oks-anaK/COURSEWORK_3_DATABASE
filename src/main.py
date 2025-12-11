from api import get_employers_hh
from config import config
from db import create_database, save_data_to_database
from dbmanager import DBManager
from processing import create_employers, create_vacancy_objects
from src.api import get_vacancies_hh_one_employer


def main():
    employers_ids = [
        "1122462",  # Skyeng
        "67611",  # Тензор
        "1993194",  # Yadro
        "733",  # Ланит
        "6591",  # Банк ПСБ
        "1740",  # Яндекс
        "9352463",  # X5-Tech
        "9418714",  # Lamoda Tech
        "665467",  # Гринатом
        "2733062",  # Лига цифровой экономики
    ]
    params = config()

    # Работодатели
    data_employers = get_employers_hh(employers_ids)
    valid_employers_list = create_employers(data_employers)

    # Вакансии работодателей
    data_vacancies = get_vacancies_hh_one_employer(employers_ids)
    changed_list_vacancies = create_vacancy_objects(data_vacancies)
    valid_vacancies_list = [
        vacancy.cast_to_dict() for vacancy in changed_list_vacancies
    ]

    # Database
    create_database("emp_and_vac", params)
    save_data_to_database(
        valid_employers_list, valid_vacancies_list, "emp_and_vac", params
    )

    # Подключение к БД
    try:
        db = DBManager(
            host=params.get("host"),
            database="emp_and_vac",
            user=params.get("user"),
            password=params.get("password"),
            port=params.get("port", 5432),
        )
        print("Подключение к БД успешно!")
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return

    # Запрос 1: Компании и количество вакансий
    if (
        input(
            "Хотите получить список всех компаний и количество вакансий у каждой компании? Введите да или нет: "
        ).lower()
        == "да"
    ):
        result = db.get_companies_and_vacancies_count()
        print("\nСписок компаний и количество вакансий:")
        print("-" * 50)
        for company, count in result:
            print(f"{company}: {count} вакансий")

    # Запрос 2: Все вакансии
    if (
        input("\nХотите получить список всех вакансий? Введите да или нет: ").lower()
        == "да"
    ):
        result = db.get_all_vacancies()
        print("\nВсе вакансии:")
        print("-" * 50)
        for company, title, salary, url in result:
            salary_str = f"{salary} руб." if salary else "Не указана"
            print(f"{company} - {title}\n  Зарплата: {salary_str}\n  Ссылка: {url}\n")

    # Запрос 3: Средняя зарплата
    if input("Хотите узнать среднюю зарплату? Введите да или нет: ").lower() == "да":
        result = db.get_avg_salary()
        avg = (
            result[0][0] if result and result[0][0] else 0
        )  # Список кортежей с одним значением
        print(f"\nСредняя зарплата по вакансиям: {avg:.2f} руб.")

    # Запрос 4: Вакансии с зарплатой выше средней
    if (
        input(
            "\nХотите получить вакансии с зарплатой выше средней? Введите да или нет: "
        ).lower()
        == "да"
    ):
        result = db.get_vacancies_with_higher_salary()
        # Дополнительная фильтрация дубликатов по названию (на случай, если в БД есть различия в пробелах/регистре)
        seen_titles = set()
        unique_vacancies = []
        for vacancy in result:
            # Нормализуем название: убираем пробелы, приводим к нижнему регистру
            title_normalized = vacancy[0].strip().lower().replace(" ", "")
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                unique_vacancies.append(vacancy)

        print(
            f"\nВакансии с зарплатой выше средней ({len(unique_vacancies)} вакансий):"
        )
        print("-" * 50)
        for vacancy in unique_vacancies:
            print(f"{vacancy[0]} - {vacancy[2]} руб. - {vacancy[4]}.")

    # Запрос 5: Поиск по ключевому слову
    if (
        input(
            "\nХотите найти вакансии по ключевому слову? Введите да или нет: "
        ).lower()
        == "да"
    ):
        keyword = input("Введите ключевое слово для поиска (например, python): ")
        result = db.get_vacancies_with_keyword(keyword)
        print(f"\nНайдено вакансий: {len(result)}")
        print("-" * 50)
        for vacancy in result:
            salary_str = "Не указана" if vacancy[2] == 0.0 else str(vacancy[2])
            print(f"{vacancy[0]} - Зарплата: {salary_str} - {vacancy[4]}.")

    # Закрываем соединение
    db.close()

    return


if __name__ == "__main__":
    main()
