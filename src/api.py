import requests
import time
import json

def get_employers_hh(employers_ids):
    data = []
    for employer_id in employers_ids:
        url = f'https://api.hh.ru/employers/{employer_id}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            vacancies = response.json()
            data.append(vacancies)
            time.sleep(0.5)  # Задержка


        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
    return data


def get_vacancies_hh_one_employer(employers_ids):
    data_vacancies = []
    for employer_id in employers_ids:
        url = f'https://api.hh.ru/vacancies?employer_id={employer_id}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            vacancies = response.json()['items']
            data_vacancies.extend(vacancies)
            time.sleep(0.5)  # Задержка


        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
    return data_vacancies





# Пример использования:
if __name__ == "__main__":
    employer_data_list = get_employers_hh(['1122462', '67611',])  # Skyeng, Тензор


    print(f"Получено {len(employer_data_list)} работодателей.")

    desired_keys = ['id', 'name', 'site_url', 'area', 'description', 'vacancies_url', 'trusted']
    all_filtered_employers = {} # Создаем словарь для хранения всех работодателей

    for employer_data in employer_data_list:
        print("-" * 50)
        employer_id = employer_data.get('id', 'N/A')
        print(f"Обработка данных для работодателя (ID: {employer_id}):")

        current_employer_filtered_info = {} # Словарь для текущего работодателя
        for key in desired_keys:
            if key == 'area':
                area_name = employer_data.get('area', {}).get('name', "Не указано")
                current_employer_filtered_info['area'] = area_name
            elif key == 'description':
                desc = employer_data.get('description', 'Нет описания')
                # Сокращаем описание, если оно длинное
                current_employer_filtered_info['description_short'] = desc[:150] + '...' if desc and len(desc) > 150 else desc
            else:
                current_employer_filtered_info[key] = employer_data.get(key, "Не указано")

        # Добавляем отфильтрованную информацию о текущем работодателе в общий словарь
        all_filtered_employers[employer_id] = current_employer_filtered_info

    print("\n\nВывод сводной информации по всем работодателям:")
    # Печатаем весь общий словарь после завершения цикла
    all_filtered_employers_json = json.dumps(all_filtered_employers, indent=4, ensure_ascii=False)

    vacancies_data_list = get_vacancies_hh_one_employer(['1122462', '67611',])
    print(json.dumps(vacancies_data_list, indent=4, ensure_ascii=False))







