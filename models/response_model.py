from pydantic import BaseModel

class ScraperRes(BaseModel):
    nome: str
    titulo: str
    preco_sem_desconto: float
    preco_com_desconto: float
    nota_avaliacao: float
    quantidade_venda: str
    quantidade_estoque: str
    nome_portal: str
    prazo_entrega: int
    valor_frete: float
