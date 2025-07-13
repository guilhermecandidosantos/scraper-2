import re
import unicodedata
from datetime import datetime
from calendar import month_name

# Mapeia nomes de meses em português para número
MESES = {
    'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'março': 3,
    'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7,
    'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
}

def normalizar(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower()

def calcular_prazo_entrega(texto: str, hoje: datetime = None) -> int :
    texto = normalizar(texto)
    hoje = hoje or datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    padrao = re.search(r'(\d{1,2}) de ([a-zç]+)', texto)
    if padrao:
        dia = int(padrao.group(1))
        mes_nome = padrao.group(2)
        mes = MESES.get(mes_nome)

        if mes is None:
            return 0  # Mês inválido

        ano = hoje.year
        data_entrega = datetime(ano, mes, dia)

        # Se a data de entrega já passou esse ano, assume que é para o próximo ano
        if data_entrega < hoje:
            data_entrega = datetime(ano + 1, mes, dia)

        return (data_entrega - hoje).days

    return 0  # Nenhuma data reconhecida
