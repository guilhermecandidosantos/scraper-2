from fastapi import APIRouter, HTTPException
from models.request_model import ScraperRequest
from models.response_scraper import ScraperResponse
from services.scraper_factory import get_scraper
from utils.domain_extractor import extract_domain
from services.db.database import create_connection
from datetime import datetime

router = APIRouter()

@router.post("/scraper", response_model=ScraperResponse)
async def extract_data(request: ScraperRequest):
    domain = extract_domain(request.link_concorrente)
    nosso_domain = extract_domain(request.nosso_link)

    try:
        scraper = await get_scraper(domain)
        dados_concorrente = await scraper.scrape(request.model_dump(), request.link_concorrente, request.cep, "concorrente")

        nosso_scraper = await get_scraper(nosso_domain)
        dados_nosso = await nosso_scraper.scrape(request.model_dump(), request.nosso_link, request.cep, "nosso")

        response_data = ScraperResponse(
            nome_concorrente = dados_concorrente.nome,
            titulo_concorrente = dados_concorrente.titulo,
            preco_sem_desconto_concorrente = dados_concorrente.preco_sem_desconto,
            preco_com_desconto_concorrente = dados_concorrente.preco_com_desconto,
            preco_sem_desconto_nosso = dados_nosso.preco_sem_desconto,
            preco_com_desconto_nosso = dados_nosso.preco_com_desconto,
            nota_avaliacao = dados_concorrente.nota_avaliacao,
            quantidade_venda = dados_concorrente.quantidade_venda,
            quantidade_estoque = dados_concorrente.quantidade_estoque,
            nome_portal = dados_concorrente.nome_portal,
            prazo_entrega_concorrente =  dados_concorrente.prazo_entrega,
            valor_frete_concorrente = dados_concorrente.valor_frete,
            prazo_entrega_nosso =  dados_nosso.prazo_entrega,
            valor_frete_nosso = dados_nosso.valor_frete
        )

        data_hora = datetime.now().isoformat()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scraper_results (
                nome_concorrente,
                titulo_concorrente,
                preco_sem_desconto_concorrente,
                preco_com_desconto_concorrente,
                preco_sem_desconto_nosso,
                preco_com_desconto_nosso,
                nota_avaliacao,
                quantidade_venda,
                quantidade_estoque,
                nome_portal,
                prazo_entrega_concorrente,
                valor_frete_concorrente,
                prazo_entrega_nosso,
                valor_frete_nosso,
                data_hora
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            response_data.nome_concorrente,
            response_data.titulo_concorrente,
            response_data.preco_sem_desconto_concorrente,
            response_data.preco_com_desconto_concorrente,
            response_data.preco_sem_desconto_nosso,
            response_data.preco_com_desconto_nosso,
            response_data.nota_avaliacao,
            response_data.quantidade_venda,
            response_data.quantidade_estoque,
            response_data.nome_portal,
            response_data.prazo_entrega_concorrente,
            response_data.valor_frete_concorrente,
            response_data.prazo_entrega_nosso,
            response_data.valor_frete_nosso,
            data_hora
        ))
        conn.commit()
        conn.close()

        return response_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
