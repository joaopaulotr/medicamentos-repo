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
location = st.text_input("Localização (opcional)", value="Brasil")
api_key = os.environ.get("SERP_APIKEY")

if not api_key:
	st.warning("A variável de ambiente SERP_APIKEY não está definida.")
else:
	if st.button("Buscar"):
		with st.spinner("Buscando resultados..."):
			params = {
				"engine": "google_shopping",
				"q": q,
				"location": location,
				"api_key": api_key
			}
			resp = requests.get("https://serpapi.com/search.json", params=params)
			if resp.status_code == 200:
				data = resp.json()
				produtos = data.get("shopping_results", [])
				if not produtos:
					st.warning("Nenhum resultado encontrado.")
				else:
					# Estruturação dos dados
					df = pd.DataFrame([
						{
							"Título": p.get("title"),
							"Preço": float(p.get("price", 0)),
							"Loja": p.get("source"),
							"Link": p.get("link"),
						}
						for p in produtos if p.get("price")
					])
					st.dataframe(df, use_container_width=True)

					# Estatísticas
					menor = df["Preço"].min()
					maior = df["Preço"].max()
					media = df["Preço"].mean()
					st.metric("Menor preço", f"R$ {menor:,.2f}")
					st.metric("Maior preço", f"R$ {maior:,.2f}")
					st.metric("Média de preços", f"R$ {media:,.2f}")

					# Gráfico de barras
					st.subheader("Distribuição de preços por loja")
					fig = px.box(df, x="Loja", y="Preço", points="all", title="Boxplot de preços por loja")
					st.plotly_chart(fig, use_container_width=True)
			else:
				st.error(f"Erro na consulta: {resp.status_code}")
