import re

def extrair_mais_numero(texto: str) -> str:
    match = re.search(r"\+?\d+", texto)
    if match:
        return match.group()
    return ""
