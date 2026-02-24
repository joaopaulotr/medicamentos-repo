"""
scraper.py
Módulo responsável por fazer web scraping dos preços de medicamentos
usando Selenium em modo headless.

Compatível com:
- Windows (local): usa Chrome + webdriver-manager
- Linux/Cloud (Streamlit Cloud, Railway, etc.): usa Chromium instalado via packages.txt
"""

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


def criar_driver():
    """
    Cria e configura o driver do Selenium em modo headless.
    Detecta automaticamente o sistema operacional para usar
    Chrome (Windows) ou Chromium (Linux/Cloud).
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    # chrome_options.add_argument("--remote-debugging-port=9222")  # Não necessário para produção
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )


    # Detecta Linux para Streamlit Cloud
    if os.name == "posix":
        binarios = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
        drivers = [
            "/usr/bin/chromedriver",
            "/usr/bin/chromium-driver",
            "/usr/lib/chromium/chromedriver",
            "/usr/lib/chromium-browser/chromedriver",
        ]
        binario = next((p for p in binarios if os.path.exists(p)), None)
        driver_path = next((p for p in drivers if os.path.exists(p)), None)
        if binario:
            chrome_options.binary_location = binario
        if driver_path:
            service = Service(driver_path)
        else:
            service = Service(ChromeDriverManager().install())
    else:
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def extrair_preco(texto_preco):
    """
    Extrai o valor numérico do preço a partir de uma string.
    Remove R$, pontos e converte vírgula para ponto.
    
    Args:
        texto_preco (str): Texto contendo o preço (ex: "R$ 199,90")
    
    Returns:
        float: Valor numérico do preço ou None se não conseguir extrair
    """
    try:
        preco_limpo = re.sub(r'[R$\s]', '', texto_preco)
        preco_limpo = preco_limpo.replace('.', '').replace(',', '.')
        return float(preco_limpo)
    except Exception:
        return None


def get_forxiga_coop():
    """
    Faz scraping do preço do Forxiga 10mg na Coop Drogaria.
    Seletores identificados via DevTools na página real.
    """
    url = "https://www.coopdrogaria.com.br/forxiga-astrazeneca-10mg--com-30-comprimidos/p"
    driver = None

    try:
        driver = criar_driver()
        driver.get(url)

        # Aguarda o container de preço carregar
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='currencyContainer']")
            )
        )

        try:
            nome_produto = driver.find_element(
                By.CSS_SELECTOR, "h1[class*='productName'], span[class*='productName']"
            ).text.strip()
        except:
            nome_produto = "Forxiga 10mg com 30 comprimidos"


        preco = None
        seletores = [
            "[class*='sellingPriceValue'] [class*='currencyContainer']",
            "[class*='sellingPrice'] [class*='currencyContainer']",
            "[class*='currencyContainer']",
            "[class*='sellingPriceValue']",
            "[class*='bestPrice']",
        ]
        for seletor in seletores:
            try:
                elemento = driver.find_element(By.CSS_SELECTOR, seletor)
                texto = elemento.text.strip()
                preco = extrair_preco(texto)
                if preco and preco > 1:
                    break
            except:
                continue
        if not preco:
            try:
                inteiro = driver.find_element(
                    By.CSS_SELECTOR, "[class*='currencyInteger']"
                ).text.strip()
                decimal = driver.find_element(
                    By.CSS_SELECTOR, "[class*='currencyDecimal']"
                ).text.strip().replace(",", "").replace(".", "")
                preco = extrair_preco(f"{inteiro},{decimal}")
            except:
                pass
        if not preco:
            return None

        return {
            "farmacia": "Coop Drogaria",
            "produto": nome_produto,
            "preco": preco,
            "url": url
        }

    except Exception:
        return None

    finally:
        if driver:
            driver.quit()


def get_forxiga_drogariasaopaulo():
    """
    Faz scraping do preço do Forxiga 10mg na Drogaria São Paulo.
    Seletor: strong.skuBestPrice
    """
    url = "https://www.drogariasaopaulo.com.br/forxiga-10mg-30-comprimidos-revestidos/p"
    driver = None

    try:
        driver = criar_driver()
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "strong.skuBestPrice"))
        )

        try:
            nome_produto = driver.find_element(
                By.CSS_SELECTOR, "h1.productName, h1[class*='productName']"
            ).text.strip()
        except:
            nome_produto = "Forxiga 10mg com 30 comprimidos"

        texto_preco = driver.find_element(
            By.CSS_SELECTOR, "strong.skuBestPrice"
        ).text.strip()
        preco = extrair_preco(texto_preco)
        if not preco:
            return None
        return {
            "farmacia": "Drogaria São Paulo",
            "produto": nome_produto,
            "preco": preco,
            "url": url
        }

    except Exception:
        return None

    finally:
        if driver:
            driver.quit()


def get_forxiga_paguemenos():
    """
    Faz scraping do preço do Forxiga 10mg no Pague Menos.
    Seletor: div[class*='paguemenos-pdp-custom-components-0-x-selling-price']
    """
    url = "https://www.paguemenos.com.br/forxiga-10mg-com-30-comprimidos/p"
    driver = None

    try:
        driver = criar_driver()
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='paguemenos-pdp-custom-components-0-x-selling-price']")
            )
        )

        try:
            nome_produto = driver.find_element(
                By.CSS_SELECTOR, "h1[class*='productName'], span[class*='productName']"
            ).text.strip()
        except:
            nome_produto = "Forxiga 10mg com 30 comprimidos"

        texto_preco = driver.find_element(
            By.CSS_SELECTOR, "[class*='paguemenos-pdp-custom-components-0-x-selling-price']"
        ).text.strip()
        preco = extrair_preco(texto_preco)
        if not preco:
            return None
        return {
            "farmacia": "Pague Menos",
            "produto": nome_produto,
            "preco": preco,
            "url": url
        }

    except Exception:
        return None

    finally:
        if driver:
            driver.quit()


def buscar_precos_forxiga():
    """
    Busca preços do Forxiga em todas as farmácias cadastradas.
    
    Returns:
        list: Lista de dicionários com os preços encontrados
    """
    resultados = []
    scrapers = [
        get_forxiga_coop,
        get_forxiga_drogariasaopaulo,
        get_forxiga_paguemenos,
    ]
    for scraper in scrapers:
        try:
            resultado = scraper()
            if resultado:
                resultados.append(resultado)
        except Exception:
            pass
    return resultados


# Dicionário de medicamentos disponíveis
MEDICAMENTOS = {
    "Forxiga 10mg (30 comp)": {
        "nome": "Forxiga 10mg com 30 comprimidos",
        "fabricante": "AstraZeneca",
        "funcao_busca": buscar_precos_forxiga
    }
    # Aqui você pode adicionar mais medicamentos no futuro
}


def buscar_precos_medicamento(nome_medicamento):
    """
    Busca preços de um medicamento específico.
    
    Args:
        nome_medicamento (str): Nome do medicamento conforme chave do dicionário MEDICAMENTOS
    
    Returns:
        list: Lista de dicionários com os preços encontrados
    """
    if nome_medicamento not in MEDICAMENTOS:
        return []
    medicamento = MEDICAMENTOS[nome_medicamento]
    funcao_busca = medicamento["funcao_busca"]
    return funcao_busca()
