from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Buscador Google Shopping", layout="wide")

st.title("🔎 Buscador Google Shopping (SerpApi)")
st.markdown("Pesquise produtos e veja estatísticas de preços!")

# Parâmetros do usuário
q = st.text_input("O que você quer buscar?", value="notebook")
location = "Sao Paulo, State of Sao Paulo, brazil"
st.caption(f"Localização fixa: {location}")
api_key = os.environ.get("SERP_APIKEY")

if not api_key:
	st.warning("A variável de ambiente SERP_APIKEY não está definida.")
else:
	if st.button("Buscar"):
		with st.spinner("Buscando resultados..."):
			params = {
                "engine": "google_shopping",
                "q": q,
                "api_key": api_key,
                "location": "Sao Paulo, State of Sao Paulo, brazil",
                "google_domain": "google.com.br",
                "gl": "br",
                "hl": "pt",
                "device": "desktop",
                "sort_by": 1,
                "no_cache": True
            }
			if location.strip():
				params["location"] = location.strip()
			resp = requests.get("https://serpapi.com/search.json", params=params)
			if resp.status_code == 200:
				data = resp.json()
				produtos = data.get("shopping_results", [])
				if not produtos:
					st.warning("Nenhum resultado encontrado.")
				else:
					# Estruturação dos dados
					def parse_price(price):
						if isinstance(price, (int, float)):
							return float(price)
						if isinstance(price, str):
							price = price.replace("R$", "").replace("$", "").replace(",", ".").strip()
							try:
								return float(price)
							except Exception:
								return None
						return None

					df = pd.DataFrame([
						{
							"Título": p.get("title"),
							"Preço": parse_price(p.get("price", 0)),
							"Loja": p.get("source"),
							"Link": p.get("link"),
						}
						for p in produtos if p.get("price")
					])

					# Formatar preço para exibição
					df["Preço_fmt"] = df["Preço"].apply(lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else "-")

					# Tabela bonita com links clicáveis
					def make_link(row):
						if row["Link"]:
							return f'<a href="{row["Link"]}" target="_blank">🔗 Ver oferta</a>'
						return "-"
					df["Oferta"] = df.apply(make_link, axis=1)

					# Badge de loja
					def loja_badge(loja):
						if not loja:
							return "-"
						cor = "#1f77b4"
						return f'<span style="background:{cor};color:#fff;padding:2px 8px;border-radius:8px;font-size:0.95em;">{loja}</span>'
					df["Loja_fmt"] = df["Loja"].apply(loja_badge)

					st.markdown("### 🛒 Resultados encontrados")
					st.write(f"<style>th,td{{text-align:center !important;}}</style>", unsafe_allow_html=True)
					st.write(
						df.to_html(
							columns=["Título", "Preço_fmt", "Loja_fmt", "Oferta"],
							escape=False,
							index=False,
							header=["Produto", "Preço", "Loja", "Oferta"]
						),
						unsafe_allow_html=True
					)

					# Estatísticas em cards
					menor = df["Preço"].min()
					maior = df["Preço"].max()
					media = df["Preço"].mean()
					col1, col2, col3 = st.columns(3)
					with col1:
						st.markdown(f"<div style='background:#eafaf1;padding:1.2em 1em;border-radius:10px;text-align:center;'><b>Menor preço</b><br><span style='font-size:2em;color:#28a745;'>R$ {menor:,.2f}</span></div>", unsafe_allow_html=True)
					with col2:
						st.markdown(f"<div style='background:#fff3cd;padding:1.2em 1em;border-radius:10px;text-align:center;'><b>Média de preços</b><br><span style='font-size:2em;color:#856404;'>R$ {media:,.2f}</span></div>", unsafe_allow_html=True)
					with col3:
						st.markdown(f"<div style='background:#fdecea;padding:1.2em 1em;border-radius:10px;text-align:center;'><b>Maior preço</b><br><span style='font-size:2em;color:#dc3545;'>R$ {maior:,.2f}</span></div>", unsafe_allow_html=True)

					# Gráfico de barras mais bonito
					st.subheader("📊 Distribuição de preços por loja")
					fig = px.bar(
						df,
						x="Loja",
						y="Preço",
						color="Loja",
						text="Preço_fmt",
						title="Preços por Loja",
						labels={"Preço": "Preço (R$)", "Loja": "Loja"},
					)
					fig.update_traces(textposition="outside")
					fig.update_layout(showlegend=False, height=450)
					st.plotly_chart(fig, use_container_width=True)
			else:
				st.error(f"Erro na consulta: {resp.status_code}")
