from datetime import datetime, timedelta
import re
import unicodedata

DIAS_SEMANA = {
    "segunda-feira": 0,
    "terca-feira": 1,
    "terça-feira": 1,
    "quarta-feira": 2,
    "quinta-feira": 3,
    "sexta-feira": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6
}

MESES = {
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

def normalizar(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower()

def extrair_data(texto):
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    texto = normalizar(texto)

    # Caso 1: formato 16/jul
    padrao_data = re.search(r'(\d{1,2})/([a-z]{3})', texto)
    if padrao_data:
        dia = int(padrao_data.group(1))
        mes = MESES.get(padrao_data.group(2))
        ano = hoje.year
        data = datetime(ano, mes, dia)
        if data < hoje:
            data = datetime(ano + 1, mes, dia)
        return (data - hoje).days

    # Novo caso: entre 22 e 23/jul
    padrao_intervalo_dois_dias = re.search(r'entre (\d{1,2}) e (\d{1,2})/([a-z]{3})', texto)
    if padrao_intervalo_dois_dias:
        dia1 = int(padrao_intervalo_dois_dias.group(1))
        dia2 = int(padrao_intervalo_dois_dias.group(2))
        mes = MESES.get(padrao_intervalo_dois_dias.group(3))
        ano = hoje.year

        datas = []
        for dia in [dia1, dia2]:
            data = datetime(ano, mes, dia)
            if data < hoje:
                data = datetime(ano + 1, mes, dia)
            datas.append(data)

        data_mais_proxima = min(datas)
        return (data_mais_proxima - hoje).days

    # Caso 2: entre terça-feira e quarta-feira 16/jul
    padrao_intervalo = re.search(r'entre .*? (\d{1,2})/([a-z]{3})', texto)
    if padrao_intervalo:
        dia = int(padrao_intervalo.group(1))
        mes = MESES.get(padrao_intervalo.group(2))
        ano = hoje.year
        data = datetime(ano, mes, dia)
        if data < hoje:
            data = datetime(ano + 1, mes, dia)
        return (data - hoje).days

    # Caso 3: apenas dia da semana (quarta-feira)
    for dia_nome, idx in DIAS_SEMANA.items():
        if dia_nome in texto:
            hoje_idx = hoje.weekday()
            dias_ate = (idx - hoje_idx + 7) % 7
            if dias_ate == 0:
                dias_ate = 7  # assume próxima ocorrência
            return dias_ate

    return None  # Nenhum padrão reconhecido
