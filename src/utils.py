from abc import ABC, abstractmethod
class Engine(ABC):
    """Абстрактный класс"""
    @abstractmethod
    def get_request(self):
        pass


    def get_vacancies(self):
        pass
