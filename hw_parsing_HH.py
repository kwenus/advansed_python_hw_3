import json
import requests
from bs4 import BeautifulSoup as bs
import fake_headers

def gen_headers():
    return fake_headers.Headers(browser='chrome', os='win').generate()

parsed_data = []
start_link = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page='
page = 0

while True:
    page_link = f"{start_link}{str(page)}"
    main_response = requests.get(page_link, headers=gen_headers())

    if main_response.status_code != 200:
        break

    main_soup = bs(main_response.text, 'lxml')
    tag_vacancies = main_soup.find_all('div', 'serp-item serp-item_link')

    for tag in tag_vacancies:
        offer_link = tag.find('a', 'bloko-link')['href']

        offer_response = requests.get(offer_link, headers=gen_headers())
        offer_soup = bs(offer_response.text, 'lxml')

        vacancy_title = offer_soup.find('div', 'vacancy-title').h1.text
        try:
            vacancy_salary = offer_soup.find('div', 'vacancy-title').span.text.replace('\xa0', '')
        except AttributeError:
            vacancy_salary = 'Зарплата не указана'

        if '$' in vacancy_salary:
            vacancy_company = offer_soup.find('div', 'vacancy-company-details').text

            try:
                vacancy_city = (offer_soup.find('div', 'vacancy-company-redesigned').
                                find('a','bloko-link bloko-link_kind-tertiary bloko-link_disable-visited').span.text)
            except AttributeError:
                vacancy_city = offer_soup.find('div', 'vacancy-company-redesigned').p.text

            try:
                vacancy_text = offer_soup.find('div', 'vacancy-description').text
            except AttributeError:
                vacancy_text = offer_soup.find('div', 'bloko-text').text

            if 'Django' and 'Flask' in vacancy_text:
                parsed_data.append({
                    'vacancy_link': offer_link,
                    'vacancy_name': vacancy_title,
                    'vacancy_salary': vacancy_salary,
                    'vacancy_company': vacancy_company,
                    'vacancy_city': vacancy_city,
                })

        else:
            continue

    # увеличиваем порядковый номер страницы
    page += 1


with open('info_parsed_HH.json', 'w') as new_file:
    json.dump(parsed_data, new_file, ensure_ascii=False)

