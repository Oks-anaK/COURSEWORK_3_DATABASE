from vacancies import Vacancy
from bs4 import BeautifulSoup
from typing import Any, Optional, Iterable, List
from api import get_vacancies_hh_one_employer
from api import get_employers_hh


def clean_html_to_text(html_text: Optional[str]) -> str:
    """Очищает HTML в текст (с использованием BeautifulSoup)."""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def create_vacancy_objects(vacancies_data: Iterable[dict[str, Any]]) -> List[Vacancy]:
    """Создает список объектов Vacancy."""
    vacancies = []

    for data in vacancies_data:
        id_vacancy = data.get("id", "")
        employer_field = data.get("employer", "")
        id_employer_vacancy = employer_field.get("id", "")
        url_employer = employer_field.get("url", "")
        title = data.get("name", "")
        salary_data = data.get("salary")
        salary_from = salary_data.get("from") if salary_data else None
        salary_to = salary_data.get("to") if salary_data else None

        snippet = data.get("snippet")
        if snippet:
            requirement_html = snippet.get("requirement")
            responsibility_html = snippet.get("responsibility")

            requirement = clean_html_to_text(requirement_html) if requirement_html else ""
            responsibility = clean_html_to_text(responsibility_html) if responsibility_html else ""

            description = (
                f"Требования: {requirement}. Обязанности: {responsibility}" if requirement or responsibility else ""
            )
        else:
            description = ""

        vacancy = Vacancy(id_vacancy, title, id_employer_vacancy, url_employer, salary_from, salary_to, description)
        vacancies.append(vacancy)

    return vacancies


def create_employers(employers_data: Iterable[dict[str, Any]]) -> List[dict[str, Any]]:
    """Создает список работодателей."""
    employers = []
    for data in employers_data:
        id_employer = data.get("id", "")
        name = data.get("name", "")
        vacancies_url = data.get("vacancies_url", "")
        # employer_field = data.get("employer", "")
        # url_employer = employer_field.get("url", "")
        description = data.get("description", "")
        valid_description = clean_html_to_text(description) if description else ""
        short_description = valid_description[:150] + '...' if valid_description and len(valid_description) > 200 else valid_description
        open_vacancies = data.get("open_vacancies", "")

        employer = {
            "id_employer": id_employer or "",
            "name_employer": name or "",
            "employer_vacancies_url": vacancies_url or "",
            "employer_description": short_description or "",
            "open_vacancies": open_vacancies or "",
        }
        employers.append(employer)
    return employers


if __name__ == '__main__':
    # vacancies_data = get_vacancies_hh_one_employer(['1122462', '67611',])
    # print(create_vacancy_objects(vacancies_data))
    employers_data = get_employers_hh(['1122462', '67611',])
    print(create_employers(employers_data))




