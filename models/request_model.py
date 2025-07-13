from pydantic import BaseModel
from typing import Literal

class ScraperRequest(BaseModel):
    link_concorrente: str
    nosso_link: str
    com_desconto_concorrente: Literal["S", "N"]
    sem_desconto_concorrente: Literal["S", "N"]
    com_desconto_nosso: Literal["S", "N"]
    sem_desconto_nosso: Literal["S", "N"]
    com_frete: Literal["S", "N"]
    com_prazo_entrega: Literal["S", "N"]
    cep: str
