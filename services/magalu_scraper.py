import re
from fastapi import HTTPException
from models.response_model import ScraperRes
from services.base_scraper import BaseScraper
from playwright.async_api import async_playwright

from utils.extrair_avaliacao_magalu import extrair_avaliacao
from utils.extrair_mais_numero import extrair_mais_numero
from utils.prazo_entrega_magalu import calcular_prazo_entrega
from utils.prazo_entrega_meli import extrair_data

class Magalu(BaseScraper):
    async def scrape(self, request_data: dict, url: str, cep: str, tipo: str) -> ScraperRes:
        nome = ""
        titulo = ""
        precoSemDesconto = 0.0
        precoComDesconto = 0.0
        notaAvaliacao = 0.0
        quantidadeEstoque = ""
        quantidadeVenda = ""
        nomePortal = "Magalu"
        prazoEntrega = 0
        valorFrete = 0.0
        erro = ""
        tipoPagina = 0

        async with async_playwright() as p: 
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="Mozilla/5.0 ...")

            pagina1 = await context.new_page()
            # await pagina1.add_init_script("""
            # Object.defineProperty(navigator, 'webdriver', {
            # get: () => false,
            # });
            # """)
            await pagina1.add_init_script("""
            Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """)
            await pagina1.wait_for_timeout(1000)
            await pagina1.goto(url)

            titulo = await pagina1.locator("h1.sc-dcJsrY.jjGTqv").inner_text()

            if(request_data["sem_desconto_concorrente"] == "S"):
                try:
                    preco = await pagina1.locator("p.sc-dcJsrY.cHdUaZ.sc-cyRcrZ.cVhyZj").inner_text(timeout=1500)
                    precoSemDesconto = re.sub(r"[^\d.]", "", preco.replace('R$', '').replace('.', '').strip().replace(',', '.'))
                except:
                    # preco = await pagina1.locator("p.sc-dcJsrY.bTcHXB.sc-iRMwjd.iHAYhf").inner_text(timeout=1500)
                    # precoSemDesconto = re.sub(r"[^\d.]", "", preco.replace('R$', '').replace('.', '').strip().replace(',', '.'))
                    precoSemDesconto = 0.00

            if(request_data["com_desconto_concorrente"] == "S"):
                preco = await pagina1.locator("p.sc-dcJsrY.bTcHXB.sc-iRMwjd.iHAYhf").inner_text(timeout=1500)
                precoComDesconto = re.sub(r"[^\d.]", "", preco.replace('R$', '').replace('.', '').strip().replace(',', '.'))

            if(tipo == "concorrente"): 
                if(request_data["com_desconto_concorrente"] == "N"):
                    precoComDesconto = 0.00
                
                if(request_data["sem_desconto_concorrente"] == "N"):
                    precoSemDesconto = 0.00

            if(tipo== "nosso"): 
                if(request_data["com_desconto_nosso"] == "N"):
                    precoComDesconto = 0.00

                if(request_data["sem_desconto_nosso"] == "N"):
                    precoSemDesconto = 0.00
                    

            notaAvaliacao = extrair_avaliacao(await pagina1.locator("span.sc-jwZKMi.ijDyWI").inner_text())


            if(request_data["com_frete"] == "S" or request_data["com_prazo_entrega"] == "S"):
                await pagina1.locator("span.sc-bWJUgm.iuVbmQ").click()

                input = pagina1.locator("#zipcode")
                await input.click()
                await input.fill(cep)

                if(request_data["com_frete"] == "S"):
                    await pagina1.wait_for_timeout(2000)
                    valorFreteStr = await pagina1.locator("p.sc-dcJsrY.eLxcFM.sc-gvPdwL.OFrmj").first.inner_text()

                    if(valorFreteStr == "Frete Grátis"):
                        valorFrete = 0.00
                else:
                    valorFrete = 0.00

                if(request_data["com_prazo_entrega"] == "S"):
                    prazoEntrega = calcular_prazo_entrega(await pagina1.locator("p.sc-dcJsrY.eLxcFM.sc-djTQaJ.ekEOGW").first.inner_text())
                else:
                    prazoEntrega = 0.00
            
            await pagina1.close()

            await browser.close()

            return ScraperRes(
                    nome = nome,
                    titulo=titulo,
                    preco_sem_desconto=float(precoSemDesconto),
                    preco_com_desconto=float(precoComDesconto),
                    nota_avaliacao=float(notaAvaliacao),
                    quantidade_estoque=quantidadeEstoque,
                    quantidade_venda=quantidadeVenda,
                    nome_portal=nomePortal,
                    prazo_entrega=prazoEntrega,
                    valor_frete=valorFrete,
            )