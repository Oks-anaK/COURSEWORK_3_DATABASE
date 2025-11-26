import os
from config import config
from api import get_employers_hh
from db import create_database
from db import save_data_to_database
from src.api import get_vacancies_hh_one_employer
from processing import create_vacancy_objects
from processing import create_employers


def main():
    employers_ids = ['1122462',  # Skyeng
                     '67611',  # Тензор
                     '1993194',  # Yadro
                     '733',  # Ланит
                     '6591',  # Банк ПСБ
                     '1740',  # Яндекс
                     '9352463',  # X5-Tech
                     '9418714',  # Lamoda Tech
                     '665467',  # Гринатом
                     '2733062',  # Лига цифровой экономики
                     ]
    params = config()

    # Работодатели
    data_employers = get_employers_hh(employers_ids)
    valid_employers_list = create_employers(data_employers)

    # Вакансии работодателей
    data_vacancies = get_vacancies_hh_one_employer(employers_ids)
    vacancies_data = get_vacancies_hh_one_employer(['1122462', '67611', ])
    changed_list_vacancies = create_vacancy_objects(vacancies_data)
    valid_vacancies_list = [vacancy.cast_to_dict() for vacancy in changed_list_vacancies]
    # print(valid_employers_list)


    # Database
    create_database('emp_and_vac', params)
    save_data_to_database(valid_employers_list, valid_vacancies_list, 'emp_and_vac', params)

    return




if __name__ == '__main__':
    main()