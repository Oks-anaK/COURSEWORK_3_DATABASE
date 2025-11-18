import os
from config import config
from db import create_database
from api import get_employers_vacancies_hh
from db import save_data_to_database


def main():
    api_key = os.getenv('API_KEY_HH')
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

    data = get_employers_vacancies_hh(api_key, employers_ids)
    create_database('', params)
    save_data_to_database(data, '', params)

    return




if __name__ == '__main__':
    main()