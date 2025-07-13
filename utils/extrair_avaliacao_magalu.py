import re

def extrair_avaliacao(texto: str) -> float | None:
    match = re.search(r'\d+(\.\d+)?', texto)
    if match:
        return float(match.group())
    return None
