from pydantic import BaseModel

class ScraperResponse(BaseModel):
    nome_concorrente: str
    titulo_concorrente: str
    preco_sem_desconto_concorrente: float
    preco_com_desconto_concorrente: float
    preco_sem_desconto_nosso: float
    preco_com_desconto_nosso: float
    nota_avaliacao: float
    quantidade_venda: str
    quantidade_estoque: str
    nome_portal: str
    prazo_entrega_concorrente: int
    valor_frete_concorrente: float
    prazo_entrega_nosso: int
    valor_frete_nosso: float
