"""
Monitor de Preços de Farmácias (Saída JSON)
===========================================
Coleta preços e URLs de medicamentos e retorna um JSON estruturado.
"""

import json
import re
import time
import sys
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
PRODUCT_QUERY = "Dapagliflozina 10mg 30 comprimidos"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def parse_price(text: str) -> float | None:
    if not text:
        return None
    cleaned = re.sub(r"[^\d,\.]", "", str(text)).replace(",", ".")
    parts = cleaned.split(".")
    if len(parts) > 2:
        cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(cleaned)
    except ValueError:
        return None

def make_record(farmacia: str, nome: str, preco: float | None, url: str) -> dict:
    return {
        "farmacia": farmacia,
        "produto": nome,
        "preco": preco,
        "url": url
    }

def init_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# ─────────────────────────────────────────────
# SCRAPERS
# ─────────────────────────────────────────────
def get_prices_drogasil(driver: webdriver.Chrome, query: str) -> list[dict]:
    base_url = "https://www.drogasil.com.br"
    search_url = f"{base_url}/search?w={query.replace(' ', '+')}"
    try:
        driver.get(search_url)
        time.sleep(3)
        next_data_json = driver.execute_script("return document.getElementById('__NEXT_DATA__')?.textContent;")
        if not next_data_json: return []
        data = json.loads(next_data_json)
        products = data["props"]["pageProps"]["pageProps"]["results"]["products"]
        records = []
        for p in products:
            p_url = p.get("url") or p.get("link") or ""
            if p_url and not p_url.startswith("http"):
                p_url = base_url + (p_url if p_url.startswith("/") else "/" + p_url)
            records.append(make_record("Drogasil", p.get("productName") or p.get("name"), parse_price(p.get("priceService")), p_url or search_url))
        return records
    except: return []

def get_prices_drogaraia(driver: webdriver.Chrome, query: str) -> list[dict]:
    base_url = "https://www.drogaraia.com.br"
    search_url = f"{base_url}/search?w={query.replace(' ', '+')}"
    try:
        driver.get(search_url)
        time.sleep(3)
        next_data_json = driver.execute_script("return document.getElementById('__NEXT_DATA__')?.textContent;")
        if not next_data_json: return []
        data = json.loads(next_data_json)
        products = data["props"]["pageProps"]["pageProps"]["results"]["products"]
        records = []
        for p in products:
            p_url = p.get("url") or p.get("link") or ""
            if p_url and not p_url.startswith("http"):
                p_url = base_url + (p_url if p_url.startswith("/") else "/" + p_url)
            records.append(make_record("Droga Raia", p.get("productName") or p.get("name"), parse_price(p.get("priceService")), p_url or search_url))
        return records
    except: return []

def get_prices_panvel(driver: webdriver.Chrome, query: str) -> list[dict]:
    search_url = f"https://www.panvel.com/panvel/buscarProduto.do?termoPesquisa={query.replace(' ', '+')}"
    try:
        driver.get(search_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.price")))
        time.sleep(2)
        products_js = driver.execute_script("""
            return Array.from(document.querySelectorAll('div.container-card-item-vertical')).map(card => ({
                name: card.querySelector('div[class*="name"]')?.innerText.trim(),
                price: card.querySelector('span.price')?.innerText.trim(),
                url: card.querySelector('a[href]')?.href
            })).filter(p => p.name && p.price);
        """)
        return [make_record("Panvel", p["name"], parse_price(p["price"]), p["url"] or search_url) for p in products_js]
    except: return []

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    query = PRODUCT_QUERY
    results = []
    driver = init_driver()

    try:
        # Coleta silenciosa (sem prints de log para não sujar o JSON)
        results.extend(get_prices_drogasil(driver, query))
        results.extend(get_prices_drogaraia(driver, query))
        results.extend(get_prices_panvel(driver, query))
        # Pague Menos (bloqueada, mas incluímos o registro de erro se desejar)
        results.append(make_record("Pague Menos", "[BLOQUEADO POR reCAPTCHA]", None, f"https://www.paguemenos.com.br/busca?q={query.replace(' ', '+')}"))
    finally:
        driver.quit()

    # Retorna o JSON final para a saída padrão
    output = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "total_resultados": len(results),
        "data": results
    }
    
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()