import re
from fastapi import HTTPException
from models.response_model import ScraperRes
from services.base_scraper import BaseScraper
from playwright.async_api import async_playwright

from utils.extrair_mais_numero import extrair_mais_numero
from utils.prazo_entrega_meli import extrair_data

class MeliScraper(BaseScraper):
    async def scrape(self, request_data: dict, url: str, cep: str, tipo: str) -> ScraperRes:
        nome = ""
        titulo = ""
        precoSemDesconto = 0.0
        precoComDesconto = 0.0
        notaAvaliacao = 0.0
        quantidadeEstoque = ""
        quantidadeVenda = ""
        nomePortal = "Mercado Livre"
        prazoEntrega = 0
        valorFrete = 0.0
        erro = ""
        tipoPagina = 0

        async with async_playwright() as p: 
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()

            pagina1 = await context.new_page()
            await pagina1.wait_for_timeout(1000)
            await pagina1.goto(url)


            erro = pagina1.locator("div.error-code")


            if(erro == "HTTP ERROR 403"):
                raise HTTPException(status_code=400, detail=str("Sem permissão para acessar a página!"))
            
            try:
                # Pagina inicial de inserir CEP
                await pagina1.locator("div.andes-form-control.andes-form-control--textfield.zip-code__textfield").inner_html(timeout=1500)
                tipoPagina = 1
            except:
                # Pagina do produto
                tipoPagina = 2
            
            if(tipoPagina == 2): 
                await pagina1.wait_for_selector("h1.ui-pdp-title", timeout=1500)

                titulo = await pagina1.locator("h1.ui-pdp-title").inner_text()

                if(request_data["com_frete"] == "S" or request_data["com_prazo_entrega" == "S"]):
                    if(request_data["cep"] is None or request_data["cep"] == ""):
                        raise HTTPException(status_code=400, detail="É obrigatório informar o frete quando a opção com_frete ou com_prazo_entrega estiver com S")

                    await pagina1.locator("a.nav-menu-cp.nav-menu-cp-logged").first.click()

                    iframe = pagina1.locator("div.andes-modal-dialog.andes-modal--loose").first.locator('iframe')

                    link = await iframe.get_attribute('src')

                    pagina2 = await context.new_page()
                    await pagina2.goto(link)
        
                    await pagina2.wait_for_timeout(1000)
                    
                    input = pagina2.locator('input.andes-form-control__field').first
                    await input.click()
                    await input.fill(cep)

                    await pagina2.wait_for_timeout(1000)

                    await pagina2.locator('button.andes-button.zip-code__use-button.andes-button--medium.andes-button--loud').click()

                    await pagina2.wait_for_timeout(1000)

                    await pagina2.close()

                    await pagina1.wait_for_timeout(1000)

                    await pagina1.reload()

                    prazoEntregaModal = pagina1.locator('div.andes-tooltip__trigger').locator('button.andes-button.seo-ui-anchor__button.ui-pdp-action-modal__link.andes-button--large.andes-button--transparent.andes-button--full-width').locator('span.andes-button__content').get_by_text('Mais formas de entrega').first

                    await prazoEntregaModal.click()

                    await pagina1.wait_for_timeout(1500)

                    iframe2 = pagina1.locator("div.andes-modal__content").first.locator('iframe')

                    link2 = await iframe2.get_attribute('src')

                    pagina3 = await context.new_page()

                    await pagina3.goto(link2)

                    await pagina3.wait_for_timeout(1000)

                    if(request_data["com_prazo_entrega"] == "S"):
                        prazo = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')  \
                                .locator('div.ui-vpp-generic-shipping')                                                \
                                .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__description')   \
                                .locator('span.ui-vpp-generic-shipping__title')                                        \
                                .locator('span.ui-pdp-color--BLACK.ui-pdp-family--SEMIBOLD').nth(0).inner_text()
                        
                        prazoEntrega = extrair_data(prazo)
                    else:
                        prazoEntrega = 0

                    if(request_data["com_frete"] == "S"):
                        try:
                            #Frete gratis
                            valorFrete = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')    \
                                                    .locator('div.ui-vpp-generic-shipping')                                          \
                                                    .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__price')   \
                                                    .locator('span.ui-pdp-color--GREEN.ui-pdp-family--REGULAR.ui-vpp-generic-shipping__price-label').nth(0).inner_text(timeout=3000)
                        except:
                            valor_frete_inteiro = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')    \
                                                            .locator('div.ui-vpp-generic-shipping')                                          \
                                                            .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__price')   \
                                                            .locator('span').locator('span').locator('span.andes-money-amount__fraction').inner_text(timeout=3000)
                            valor_frete_centavo = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')    \
                                                            .locator('div.ui-vpp-generic-shipping')                                          \
                                                            .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__price')   \
                                                            .locator('span').locator('span').locator('span.andes-money-amount__cents').inner_text(timeout=3000)
                            valorFrete = valor_frete_inteiro + "." + valor_frete_centavo
                                                
                        if(valorFrete == 'Grátis'): 
                            valorFrete = 0
                    else:
                        valorFrete = 0

                    await pagina3.close()

            elif(tipoPagina == 1):
                await pagina1.wait_for_selector("h1.ui-pdp-title", timeout=1500)

                titulo = await pagina1.locator("h1.ui-pdp-title").inner_text()

                await pagina1.wait_for_timeout(1000)
                input = pagina1.locator('input.andes-form-control__field').first
                await input.click()
                await input.fill(cep)

                await pagina1.locator('button.andes-button.zip-code__use-button.andes-button--medium.andes-button--loud').click()

                await pagina1.get_by_text('Mais formas de entrega').first.click()

                pagina1.wait_for_selector("h1.ui-pdp-title", timeout=1500)
                await pagina1.wait_for_timeout(1500)

                prazoEntregaModal = pagina1.locator('div.andes-tooltip__trigger').locator('button.andes-button.seo-ui-anchor__button.ui-pdp-action-modal__link.andes-button--large.andes-button--transparent.andes-button--full-width').locator('span.andes-button__content').get_by_text('Mais formas de entrega').first

                await prazoEntregaModal.click()

                await pagina1.wait_for_timeout(1500)

                iframe2 = pagina1.locator("div.andes-modal__content").first.locator('iframe')

                link2 = await iframe2.get_attribute('src')

                pagina3 = await context.new_page()

                await pagina3.goto(link2)

                await pagina3.wait_for_timeout(1000)

                if(request_data["com_prazo_entrega"] == "S"):
                    prazo = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')  \
                            .locator('div.ui-vpp-generic-shipping')                                                \
                            .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__description')   \
                            .locator('span.ui-vpp-generic-shipping__title')                                        \
                            .locator('span.ui-pdp-color--BLACK.ui-pdp-family--SEMIBOLD').nth(0).inner_text()
                    
                    prazoEntrega = extrair_data(prazo)
                else:
                    prazoEntrega = 0

                if(request_data["com_frete"] == "S"):
                    try:
                        #Frete gratis
                        valorFrete = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')    \
                                                .locator('div.ui-vpp-generic-shipping')                                          \
                                                .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__price')   \
                                                .locator('span.ui-pdp-color--GREEN.ui-pdp-family--REGULAR.ui-vpp-generic-shipping__price-label').nth(0).inner_text(timeout=3000)
                    except:
                        valor_frete_inteiro = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')    \
                                                        .locator('div.ui-vpp-generic-shipping')                                          \
                                                        .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__price')   \
                                                        .locator('span').locator('span').locator('span.andes-money-amount__fraction').inner_text(timeout=3000)
                        valor_frete_centavo = await pagina3.locator('div.ui-pdp-container__row.ui-pdp-container__row--address-shipping')    \
                                                        .locator('div.ui-vpp-generic-shipping')                                          \
                                                        .locator('div.ui-vpp-generic-shipping__column.ui-vpp-generic-shipping__price')   \
                                                        .locator('span').locator('span').locator('span.andes-money-amount__cents').inner_text(timeout=3000)
                        valorFrete = valor_frete_inteiro + "." + valor_frete_centavo
                                            
                    if(valorFrete == 'Grátis'): 
                        valorFrete = 0
                else:
                    valorFrete = 0

                await pagina3.close()

            try:
                notaAvaliacao = await pagina1.locator("span.ui-pdp-review__rating").first.inner_text(timeout=1500)
            except:
                notaAvaliacao = 0.0

            nome = await pagina1.locator("h2.ui-pdp-color--BLACK.ui-pdp-size--LARGE.ui-pdp-family--SEMIBOLD.ui-seller-data-header__title.non-selectable").inner_text()
            
            quantidadeVenda = extrair_mais_numero(await pagina1.locator("span.ui-pdp-subtitle").inner_text())
            quantidadeEstoque = extrair_mais_numero(await pagina1.locator("span.ui-pdp-buybox__quantity__available").inner_text(timeout=1500))

            try:
                preco = await pagina1.locator("s.andes-money-amount.ui-pdp-price__part.ui-pdp-price__original-value.andes-money-amount--previous.andes-money-amount--cents-superscript.andes-money-amount--compact").inner_text(timeout=1500)
                precoSemDesconto = re.sub(r"[^\d.]", "", preco.replace('R$', '').replace('.', '').strip().replace(',', '.'))
                precoSemDescontoExiste = 1
            except:
                precoSemDescontoExiste = 0

            if(precoSemDescontoExiste == 0):
                preco = await pagina1.locator("div.ui-pdp-price__second-line").locator('[data-testid="price-part"]').locator("span.andes-money-amount.ui-pdp-price__part.andes-money-amount--cents-superscript.andes-money-amount--compact").inner_text()

                precoSemDesconto = re.sub(r"[^\d.]", "", preco.replace('R$', '').replace('.', '').strip().replace(',', '.'))
            elif(precoSemDescontoExiste == 1):
                preco = await pagina1.locator("div.ui-pdp-price__second-line").locator('[data-testid="price-part"]').locator("span.andes-money-amount.ui-pdp-price__part.andes-money-amount--cents-superscript.andes-money-amount--compact").inner_text()

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