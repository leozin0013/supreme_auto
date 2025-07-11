import requests
from bs4 import BeautifulSoup
import re
import json

def get_estoque_from_urls(urls_json):
    """
    Recebe uma string JSON com uma lista de URLs e retorna a soma dos estoques encontrados.
    """
    try:
        urls = json.loads(urls_json)
        if not isinstance(urls, list):
            print(f"Formato de URLs inválido: {urls_json}")
            return 0
    except Exception as e:
        print(f"Erro ao decodificar JSON das URLs: {urls_json} - {e}")
        return 0
    total = 0
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            elemento = soup.find(class_='ui-pdp-buybox__quantity')
            if elemento:
                texto = elemento.text.strip()
                if texto != "Último disponível!":
                    elemento = soup.find(class_='ui-pdp-buybox__quantity__available')
                    if elemento:
                        texto = elemento.text.strip()
                        somente_numeros = re.sub(r'\D', '', texto)
                        if somente_numeros != '':
                            total += int(somente_numeros)
                else:
                    total += 1
            # Se não encontrar, considera 0
        except Exception as e:
            print(f"Erro ao buscar estoque da URL {url}: {e}")
    return total