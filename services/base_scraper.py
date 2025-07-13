from abc import ABC, abstractmethod
from models.response_model import ScraperRes

class BaseScraper(ABC):
    @abstractmethod
    # def scrape(self, request_data: dict) -> ScraperRes:
    def scrape(self, request_data:dict, url: str, cep: str, tipo: str) -> ScraperRes:
        """Método abstrato que precisa ser implementado nas subclasses"""
        raise NotImplementedError
