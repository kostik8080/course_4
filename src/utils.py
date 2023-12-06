from abc import ABC, abstractmethod

import requests


class ParsingError(Exception):
    def __str__(self):
        return "Ошибка подключения по API"


class Engine(ABC):
    """Абстрактный класс"""

    @abstractmethod
    def get_request(self):
        pass

    def get_vacancies(self):
        pass


class HeadHunter(Engine):
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
            formated_salary[0] = salary["from"] if salary["currency"].lower == "rur" else salary["from"] * 76
        if salary and salary["to"] and salary["to"] != 0:
            formated_salary[1] = salary["to"] if salary["currency"].lower == "rur" else salary["to"] * 76
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
