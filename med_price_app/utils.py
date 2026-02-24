"""
utils.py
Funções utilitárias para cálculos e análises de preços
"""

import pandas as pd
from typing import List, Dict, Optional


def calcular_media_precos(lista_precos: List[Dict]) -> Optional[float]:
    """
    Calcula a média dos preços de uma lista de resultados.
    
    Args:
        lista_precos (List[Dict]): Lista de dicionários contendo 'preco'
        
    Returns:
        float: Média dos preços ou None se lista vazia
    """
    if not lista_precos:
        return None
    
    precos = [item['preco'] for item in lista_precos if 'preco' in item and item['preco']]
    
    if not precos:
        return None
    
    return sum(precos) / len(precos)


def menor_preco(lista_precos: List[Dict]) -> Optional[Dict]:
    """
    Encontra o item com menor preço.
    
    Args:
        lista_precos (List[Dict]): Lista de dicionários contendo 'preco'
        
    Returns:
        Dict: Dicionário completo do item com menor preço ou None
    """
    if not lista_precos:
        return None
    
    precos_validos = [item for item in lista_precos if 'preco' in item and item['preco']]
    
    if not precos_validos:
        return None
    
    return min(precos_validos, key=lambda x: x['preco'])


def maior_preco(lista_precos: List[Dict]) -> Optional[Dict]:
    """
    Encontra o item com maior preço.
    
    Args:
        lista_precos (List[Dict]): Lista de dicionários contendo 'preco'
        
    Returns:
        Dict: Dicionário completo do item com maior preço ou None
    """
    if not lista_precos:
        return None
    
    precos_validos = [item for item in lista_precos if 'preco' in item and item['preco']]
    
    if not precos_validos:
        return None
    
    return max(precos_validos, key=lambda x: x['preco'])


def criar_dataframe_precos(lista_precos: List[Dict]) -> pd.DataFrame:
    """
    Converte lista de preços em DataFrame do pandas para exibição.
    
    Args:
        lista_precos (List[Dict]): Lista de dicionários com dados dos preços
        
    Returns:
        pd.DataFrame: DataFrame organizado com os dados
    """
    if not lista_precos:
        return pd.DataFrame()
    
    df = pd.DataFrame(lista_precos)
    
    # Formata a coluna de preço
    if 'preco' in df.columns:
        df['preco_formatado'] = df['preco'].apply(lambda x: f"R$ {x:.2f}")
    
    # Reorganiza colunas na ordem desejada
    colunas_ordem = ['farmacia', 'preco_formatado', 'produto', 'url']
    colunas_existentes = [col for col in colunas_ordem if col in df.columns]
    
    return df[colunas_existentes]


def calcular_economia(lista_precos: List[Dict]) -> Optional[float]:
    """
    Calcula quanto você economiza comprando no menor preço em vez da média.
    
    Args:
        lista_precos (List[Dict]): Lista de dicionários contendo 'preco'
        
    Returns:
        float: Valor da economia ou None
    """
    if not lista_precos or len(lista_precos) < 2:
        return None
    
    media = calcular_media_precos(lista_precos)
    menor = menor_preco(lista_precos)
    
    if not media or not menor:
        return None
    
    economia = media - menor['preco']
    
    return economia if economia > 0 else 0


def calcular_percentual_diferenca(lista_precos: List[Dict]) -> Optional[float]:
    """
    Calcula o percentual de diferença entre o maior e menor preço.
    
    Args:
        lista_precos (List[Dict]): Lista de dicionários contendo 'preco'
        
    Returns:
        float: Percentual de diferença ou None
    """
    if not lista_precos or len(lista_precos) < 2:
        return None
    
    menor = menor_preco(lista_precos)
    maior = maior_preco(lista_precos)
    
    if not menor or not maior or menor['preco'] == 0:
        return None
    
    diferenca_percentual = ((maior['preco'] - menor['preco']) / menor['preco']) * 100
    
    return diferenca_percentual


def formatar_moeda(valor: float) -> str:
    """
    Formata um valor numérico como moeda brasileira.
    
    Args:
        valor (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado (ex: "R$ 199,90")
    """
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')


def gerar_estatisticas(lista_precos: List[Dict]) -> Dict:
    """
    Gera um dicionário completo com todas as estatísticas dos preços.
    
    Args:
        lista_precos (List[Dict]): Lista de dicionários contendo 'preco'
        
    Returns:
        Dict: Dicionário com todas as estatísticas
    """
    if not lista_precos:
        return {
            "total_fontes": 0,
            "media": None,
            "menor": None,
            "maior": None,
            "economia": None,
            "diferenca_percentual": None
        }
    
    return {
        "total_fontes": len(lista_precos),
        "media": calcular_media_precos(lista_precos),
        "menor": menor_preco(lista_precos),
        "maior": maior_preco(lista_precos),
        "economia": calcular_economia(lista_precos),
        "diferenca_percentual": calcular_percentual_diferenca(lista_precos)
    }
