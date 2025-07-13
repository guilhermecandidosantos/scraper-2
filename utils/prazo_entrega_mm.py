from datetime import datetime
import re
import locale

# Define o locale para português do Brasil (para reconhecer meses em português)
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    # Em alguns sistemas (Windows ou WSL), pode precisar ajustar ou ignorar
    pass

def calcular_prazo_entrega(texto: str) -> int:
    # Expressão regular para encontrar a data no formato "01 de agosto"
    match = re.search(r'(\d{1,2}) de ([a-zç]+)', texto, re.IGNORECASE)
    if not match:
        return 0  # ou lançar erro se preferir

    dia_str, mes_str = match.groups()

    dia = int(dia_str)
    mes_nome = mes_str.lower()

    # Mapeia nomes dos meses para número do mês
    meses = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }

    mes = meses.get(mes_nome)
    if not mes:
        return 0  # mês inválido

    hoje = datetime.today()
    ano = hoje.year

    # Ajusta o ano se a data de entrega já passou no ano atual
    data_entrega = datetime(ano, mes, dia)
    if data_entrega < hoje:
        data_entrega = datetime(ano + 1, mes, dia)

    prazo = (data_entrega.date() - hoje.date()).days
    return prazo
