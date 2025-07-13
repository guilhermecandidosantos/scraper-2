from fastapi import HTTPException
from playwright.async_api import async_playwright
from models.response_model import ScraperRes
from utils.extrair_mais_numero import extrair_mais_numero
from utils.prazo_entrega_mm import calcular_prazo_entrega
from .base_scraper import BaseScraper
import re

class MMScraper(BaseScraper):
    async def scrape(self, request_data: dict, url: str, cep: str, tipo: str) -> ScraperRes:

        async with async_playwright() as p:
            nome = ""
            titulo = ""
            precoSemDesconto = 0.0
            precoComDesconto = 0.0
            notaAvaliacao = 0.0
            quantidadeEstoque = ""
            quantidadeVenda = ""
            nomePortal = "Madeira Madeira"
            prazoEntrega = 0
            valorFrete = 0.0
            erro = ""
            tipoPagina = 0

            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            pagina1 = await context.new_page()
            await pagina1.goto(url)

            await pagina1.wait_for_selector("h1.cav--c-fpAEqe")
            titulo = await pagina1.locator("h1.cav--c-fpAEqe").text_content()
            nome = await pagina1.locator("p.cav--c-gNPphv.cav--c-gNPphv-jBYPmg-textStyle-bodySmallSemibold.cav--c-gNPphv-idvyejX-css").inner_text(timeout=1500)

            preco = await pagina1.locator("span.cav--c-gNPphv.cav--c-gNPphv-iELazp-textStyle-h3Semibold.cav--c-gNPphv-hHqInm-size-h3").inner_text()
            precoSemDesconto = re.sub(r"[^\d.]", "", preco.replace('R$', '').replace('.', '').strip().replace(',', '.'))
            
            if(request_data["com_desconto_concorrente"] == "S") or request_data["com_desconto_nosso"]:
                try:
                    preco = await pagina1.locator("span.cav--c-gNPphv.cav--c-gNPphv-ieGIEOA-css").inner_text(timeout=2000)
                    precoComDesconto = re.sub(r"[^\d.]", "", preco.replace('R$', '').replace('.', '').strip().replace(',', '.'))
                except:
                    precoComDesconto = 0.00
                    
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

            notaAvaliacao = await pagina1.locator("span.cav--c-gNPphv.cav--c-gNPphv-kVkYWK-size-bodySmall.cav--c-gNPphv-hyvuql-weight-bold.cav--c-gNPphv-ifVKOYk-css").inner_text()

            try:
                qtde_disp = await pagina1.locator("div.cav--c-lesPJm.cav--c-IcOXF").locator("p.cav--c-gNPphv.cav--c-gNPphv-kVkYWK-size-bodySmall").inner_text()
            except:
                quantidadeEstoque = "Não informado"

            if(qtde_disp == "Em estoque"):
              quantidadeEstoque = "Não informado"
            else:
              quantidadeEstoque = re.sub(r'\D', '', qtde_disp)

            quantidadeVenda = "0"
            
            if(request_data["com_frete"] == "S" or request_data["com_prazo_entrega"] == "S"):
              if(request_data["cep"] is None or request_data["cep"] == ""):
                        raise HTTPException(status_code=400, detail="É obrigatório informar o frete quando a opção com_frete ou com_prazo_entrega estiver com S")
              
              input = pagina1.locator('input.cav--c-iQquop.cav--c-iQquop-kBWBEd-labelIcon-false').first
              await input.click()
              await input.fill(cep)
              

              await pagina1.locator("button.cav--c-iOefvc.cav--c-iOefvc-kAkgtL-variant-secondary.cav--c-iOefvc-idykQLZ-css.button__freight--calculate").click()

              await pagina1.wait_for_selector("p.cav--c-gNPphv.cav--c-gNPphv-iNbZ-textStyle-bodyMediumBold.cav--c-gNPphv-idXPgfK-css")

              valor_frete_str = await pagina1.locator("p.cav--c-gNPphv.cav--c-gNPphv-iNbZ-textStyle-bodyMediumBold.cav--c-gNPphv-idXPgfK-css").inner_text()

              if(valor_frete_str == "GRÁTIS"):
                  valorFrete = 0
              else:
                  valorFrete = float(re.sub(r"[^\d.]", "", valor_frete_str.replace('R$', '').replace('.', '').strip().replace(',', '.')))

              prazo = await pagina1.locator("div.cav--c-gqwkJN.cav--c-gqwkJN-iTKOFX-direction-column.cav--c-gqwkJN-iHhAvo-css")  \
                          .locator("p.cav--c-gNPphv.cav--c-gNPphv-epiGtV-textStyle-bodySmallRegular").inner_text()

              
              prazoEntrega = calcular_prazo_entrega(prazo)


            else:
                valorFrete = 0
            
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

        