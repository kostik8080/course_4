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


    def get_request(self):
        """
        Получение значений через API
        """
        response = requests.get("https://api.hh.ru/vacancies", headers=self.__header, params=self.__params)
        if response.status_code != 200:
            raise ParsingError
        return response.json()["items"]
