from services.magalu_scraper import Magalu
from services.meli_scraper import MeliScraper
from services.mm_scraper import MMScraper
from .base_scraper import BaseScraper

async def get_scraper(domain: str) -> BaseScraper:
    if "www.mercadolivre.com.br" in domain or "produto.mercadolivre.com.br" in domain:
        return MeliScraper()
    if "www.madeiramadeira.com.br" in domain:
        return MMScraper()
    if "www.magazineluiza.com.br" in domain:
        return Magalu()
    raise ValueError("Domínio não suportado")
