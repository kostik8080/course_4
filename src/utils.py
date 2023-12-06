import json
import os
from abc import ABC, abstractmethod

import requests


class ParsingError(Exception):
    def __str__(self):
        return "Ошибка подключения по API"


class Vacancy:
    __slots__ = ("vacancy_id", "title", "url", "salary_from", "salary_to", "employer", "api")

    def __init__(self, vacancy_id, title, url, salary_from, salary_to, employer, api):
        self.vacancy_id = vacancy_id
        self.title = title
        self.url = url
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.employer = employer
        self.api = api

    """
        Сортировка вакансий
    """

    def __gt__(self, other):
        if not other.salary_from:
            return True
        elif not self.salary_from:
            return False
        return self.salary_from >= other.salary_from

    def __str__(self):
        salary_from = f"От {self.salary_from}" if self.salary_from else ''
        salary_to = f"до {self.salary_to}" if self.salary_to else ""
        if self.salary_from is None and salary_to is None:
            salary_from = "Не указано"
        return f'Вакансия: \"{self.title}"\nКомпания: \"{self.employer}"\nЗарплата: {salary_from} {salary_to} \nURL: {self.url}'


class Connector:
    '''Создание класса для работы с json файлом с вакансиями'''

    def __init__(self, keyword, vacancies_json):
        self.__filename = f'{keyword.title()}.json'
        self.insert(vacancies_json)

    def insert(self, vacancies_json):
        ''' Внесение данных о вакансиях в json файл '''
        with open(self.__filename, 'w', encoding='utf-8') as file:
            json.dump(vacancies_json, file, ensure_ascii=False, indent=4)

    def select(self):
        ''' Извлечение из json файла данных о вакансии с заданными параметрами '''
        with open(self.__filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        vacancies = [Vacancy(x['id'], x['title'], x['url'], x['salary_from'], x['salary_to'], x['employer'], x['api'])
                     for x in data]
        return vacancies

    def sorted_vacancies_by_salary_from_asc(self):
        ''' Сортировка вакансий по минимальным зарплатам по возрастающей'''
        vacancies = self.select()
        vacancies = sorted(vacancies, key=lambda p: p.salary_from or 0)
        return vacancies

    def sorted_vacancies_by_salary_from_desc(self):
        ''' Сортировка вакансий по минимальным зарплатам по убывающей'''
        vacancies = self.select()
        vacancies = sorted(vacancies, reverse=True, key=lambda p: p.salary_from or 0)
        return vacancies

    def sorted_vacancies_by_salary_to_asc(self):
        ''' Сортировка по максимальным заррплатам'''
        vacancies = self.select()
        vacancies = sorted(vacancies, key=lambda x: x.salary_to if x.salary_to else 0)
        return vacancies


class Engine(ABC):
    """Абстрактный класс"""

    @abstractmethod
    def get_request(self):
        pass

    def get_vacancies(self):
        pass


class HeadHunter(Engine):
    """
    Класс API по hh.ru
    """

    def __init__(self, keyword):
        self.keyword = keyword
        self.__header = {
            "User-Agent": "kostik80_80@mail.ru"}
        self.__params = {
            "text": keyword,
            "page": 0,
            "per_page": 100,
        }
        self.__vacancies = []  # список вакансий, который заполняется  по мерере получения данных по api

    @staticmethod
    def get_salary(salary):
        formated_salary = [None, None]
        if salary and salary["from"] and salary["from"] != 0:
            formated_salary[0] = salary["from"] if salary["currency"].lower == "rur" else salary["from"]
        if salary and salary["to"] and salary["to"] != 0:
            formated_salary[1] = salary["to"] if salary["currency"].lower == "rur" else salary["to"]
        return formated_salary

    def get_request(self):
        """
        Получение значений через API
        """
        response = requests.get("https://api.hh.ru/vacancies", headers=self.__header, params=self.__params)
        if response.status_code != 200:
            raise ParsingError
        return response.json()["items"]

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        for vacancy in self.__vacancies:
            salary_from, salary_to = self.get_salary(vacancy["salary"])
            formatted_vacancies.append({
                "id": vacancy["id"],
                "title": vacancy["name"],
                "url": vacancy["alternate_url"],
                "salary_from": salary_from,
                "salary_to": salary_to,
                "employer": vacancy["employer"]["name"],
                "api": "HeadHunter",
            })
        return formatted_vacancies

    def get_vacancies(self, pages_count=1):
        while self.__params["page"] < pages_count:
            print(f"HeadHunter, Парсинг страницы {self.__params['page'] + 1}", end=": ")
            try:
                values = self.get_request()
            except ParsingError:
                print("Ошибка при получении данных")
                break
            print(f"Найдено ({len(values)}) вакансий")
            self.__vacancies.extend(values)
            self.__params["page"] += 1


class SuperJob(Engine, ABC):
    __API_KEY = os.getenv("SUPERJOB_APIKEY")

    def __init__(self, keyword):
        self.keyword = keyword
        self.__header = {"X-Api-App-Id": self.__API_KEY}
        self.__params = {
            "keyword": keyword,
            "page": 0,
            "count": 100,
        }
        self.__vacancies = []

    @staticmethod
    def get_salary(salary, currency):
        formatted_salary = None
        if salary and salary != 0:
            formatted_salary = salary if currency == 'rub' else salary['from']
        return formatted_salary

    def get_request(self):
        response = requests.get("https://api.superjob.ru/2.0/vacancies/",
                                headers=self.__header,
                                params=self.__params)
        if response.status_code != 200:
            raise ParsingError
        return response.json()['objects']

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        for vacancy in self.__vacancies:
            formatted_vacancies.append({
                "id": vacancy["id"],
                "title": vacancy["profession"],
                "url": vacancy["link"],
                "salary_from": self.get_salary(vacancy['payment_from'], vacancy['currency']),
                "salary_to": self.get_salary(vacancy['payment_to'], vacancy['currency']),
                "employer": vacancy['firm_name'],
                "api": "SuperJob",
            })
        return formatted_vacancies

    def get_vacancies(self, pages_count=1):
        while self.__params['page'] < pages_count:
            print(f"SuperJob, Парсинг страницы {self.__params['page'] + 1}", end=": ")
            try:
                values = self.get_request()
            except ParsingError:
                print("Ошибка при получении данных")
                break
            print(f"Найдено ({len(values)}) вакансий.")
            self.__vacancies.extend(values)
            self.__params['page'] += 1
