from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Buscador Google Shopping", layout="wide")

# ── CSS Global ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 80% 80%, rgba(236,72,153,0.10) 0%, transparent 50%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1400px; }

/* ── Hero ── */
.hero-header { text-align: center; padding: 3.5rem 0 2.5rem; }
.hero-tag {
    display: inline-block; font-size: 0.7rem; font-weight: 500; letter-spacing: 0.25em;
    text-transform: uppercase; color: #818cf8; background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25); padding: 0.35rem 1rem;
    border-radius: 100px; margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif; font-size: clamp(2.4rem, 5vw, 4rem); font-weight: 800;
    line-height: 1.1; letter-spacing: -0.03em; color: #f8fafc; margin: 0 0 0.75rem;
}
.hero-title span {
    background: linear-gradient(135deg, #818cf8 0%, #ec4899 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { font-size: 1.05rem; color: #94a3b8; font-weight: 300; margin: 0; }

/* ── Search row ── */
.search-row {
    display: flex; gap: 1rem; align-items: flex-end;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 1.75rem 2rem; margin: 1.75rem 0 0.5rem;
    backdrop-filter: blur(12px); position: relative;
}

/* Input overrides */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important; color: #f1f5f9 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    padding: 0.75rem 1.1rem !important; transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    background: rgba(99,102,241,0.07) !important;
}
.stTextInput > div > div > input::placeholder { color: #475569 !important; }
.stTextInput label {
    color: #94a3b8 !important; font-size: 0.78rem !important; font-weight: 500 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.95rem !important; letter-spacing: 0.04em !important; border: none !important;
    border-radius: 12px !important; padding: 0.72rem 2rem !important; width: 100% !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.5) !important;
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Caption */
.stCaption { color: #4b5563 !important; font-size: 0.74rem !important; }

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700;
    color: #f1f5f9; letter-spacing: -0.02em; margin: 2rem 0 1rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.section-heading::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.4), transparent);
}

/* Results badge */
.results-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-size: 0.76rem; font-weight: 500; color: #818cf8;
    background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2);
    padding: 0.28rem 0.8rem; border-radius: 100px; letter-spacing: 0.04em; margin-bottom: 1rem;
}

/* ── Product Table ── */
.product-table-wrapper {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; overflow: hidden; margin-bottom: 1.5rem;
}
.product-table-wrapper table { width: 100%; border-collapse: collapse; font-family: 'DM Sans', sans-serif; }
.product-table-wrapper thead tr {
    background: rgba(99,102,241,0.1); border-bottom: 1px solid rgba(99,102,241,0.2);
}
.product-table-wrapper thead th {
    padding: 0.85rem 1.1rem; text-align: left; font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase; color: #818cf8;
}
.product-table-wrapper thead th:first-child { width: 72px; text-align: center; }
.product-table-wrapper tbody tr {
    border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s ease;
}
.product-table-wrapper tbody tr:hover { background: rgba(255,255,255,0.04); }
.product-table-wrapper tbody tr:last-child { border-bottom: none; }
.product-table-wrapper tbody td {
    padding: 0.7rem 1.1rem; font-size: 0.87rem; color: #cbd5e1; vertical-align: middle;
}
/* Produto title col */
.product-table-wrapper tbody td:nth-child(2) {
    color: #f1f5f9; max-width: 340px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
/* Price col */
.product-table-wrapper tbody td:nth-child(3) {
    font-family: 'Syne', sans-serif; font-weight: 600; color: #a5b4fc; white-space: nowrap;
}

/* Thumbnail */
.thumb-cell { text-align: center; padding: 0.5rem 0.75rem !important; }
.thumb-img {
    width: 50px; height: 50px; object-fit: contain; border-radius: 10px;
    background: rgba(255,255,255,0.07); padding: 4px;
    border: 1px solid rgba(255,255,255,0.1); display: block; margin: 0 auto;
    transition: transform 0.2s ease;
}
.thumb-img:hover { transform: scale(1.15); }
.thumb-placeholder {
    width: 50px; height: 50px; border-radius: 10px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto; font-size: 1.2rem; color: #475569;
}

/* Store badge */
.store-badge {
    display: inline-block; font-size: 0.76rem; font-weight: 500; color: #94a3b8;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    padding: 0.18rem 0.55rem; border-radius: 6px; letter-spacing: 0.02em; white-space: nowrap;
}

/* Offer link */
a.offer-link {
    display: inline-flex; align-items: center; gap: 0.3em; font-size: 0.78rem; font-weight: 500;
    color: #818cf8; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2);
    padding: 0.22rem 0.65rem; border-radius: 6px; text-decoration: none; letter-spacing: 0.02em;
    transition: background 0.15s, border-color 0.15s; white-space: nowrap;
}
a.offer-link:hover { background: rgba(99,102,241,0.22); border-color: rgba(99,102,241,0.45); color: #a5b4fc; }

/* ── Pagination ── */
.pagination-bar {
    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    padding: 1rem 0 1.5rem;
}
.page-info {
    font-size: 0.78rem; color: #64748b; letter-spacing: 0.04em;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    padding: 0.3rem 0.85rem; border-radius: 8px;
}

/* Stat cards */
.stat-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1.5rem 1.75rem; text-align: center;
    position: relative; overflow: hidden; transition: transform 0.2s ease, border-color 0.2s ease;
}
.stat-card:hover { transform: translateY(-3px); border-color: rgba(99,102,241,0.3); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.stat-card.min::before { background: linear-gradient(90deg, #10b981, #34d399); }
.stat-card.avg::before { background: linear-gradient(90deg, #6366f1, #818cf8); }
.stat-card.max::before { background: linear-gradient(90deg, #ec4899, #f43f5e); }
.stat-label {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase;
    color: #64748b; margin-bottom: 0.5rem;
}
.stat-value {
    font-family: 'Syne', sans-serif; font-size: 1.65rem; font-weight: 800;
    letter-spacing: -0.03em; line-height: 1;
}
.stat-card.min .stat-value { color: #34d399; }
.stat-card.avg .stat-value { color: #818cf8; }
.stat-card.max .stat-value { color: #f472b6; }

/* Currency note */
.currency-note {
    font-size: 0.72rem; color: #475569; background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06); padding: 0.2rem 0.65rem;
    border-radius: 6px; margin-left: 0.5rem; font-weight: 400; letter-spacing: 0;
}

.stSpinner > div { border-top-color: #6366f1 !important; }
.js-plotly-plot .plotly, .plot-container { background: transparent !important; }
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Hide ugly streamlit empty element gaps */
div[data-testid="stVerticalBlock"] > div:empty { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-tag">⚡ Powered by SerpApi · Google Shopping</div>
    <h1 class="hero-title">Busca <span>Inteligente</span><br>de Produtos</h1>
    <p class="hero-sub">Compare preços em tempo real e encontre as melhores ofertas</p>
</div>
""", unsafe_allow_html=True)

# ── Search Row ───────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    q = st.text_input("O que você quer buscar?", value="notebook", label_visibility="visible")
with col_btn:
    # pequeno spacer via markdown para alinhar botão com o input
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    search_clicked = st.button("🔍 Buscar")

location = "Sao Paulo, State of Sao Paulo, brazil"
st.caption(f"📍 Localização fixa: {location}")

# ── Pagination state ─────────────────────────────────────────────────────────
ROWS_PER_PAGE = 10

if "df_results" not in st.session_state:
    st.session_state.df_results = None
if "page" not in st.session_state:
    st.session_state.page = 0
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# ── Main Logic ───────────────────────────────────────────────────────────────
api_key = os.environ.get("SERP_APIKEY")
if not api_key:
    st.warning("A variável de ambiente SERP_APIKEY não está definida.")
else:
    if search_clicked:
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
                    st.session_state.df_results = None
                else:
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
                            "Preço": float(p["extracted_price"]) if p.get("extracted_price") is not None else parse_price(p.get("price", 0)),
                            "Loja": p.get("source"),
                            "Link": p.get("link"),
                            "Thumbnail": p.get("thumbnail", ""),
                        }
                        for p in produtos if p.get("price")
                    ])

                    st.session_state.df_results = df
                    st.session_state.page = 0
                    st.session_state.last_query = q
            else:
                st.error(f"Erro na consulta: {resp.status_code}")

    # ── Display results if available ─────────────────────────────────────────
    if st.session_state.df_results is not None:
        df = st.session_state.df_results
        total = len(df)
        total_pages = max(1, -(-total // ROWS_PER_PAGE))  # ceil division
        page = st.session_state.page

        # Slice for current page
        start = page * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        df_page = df.iloc[start:end].copy()

        # ── Format columns ────────────────────────────────────────────────
        df_page["Preço_fmt"] = df_page["Preço"].apply(
            lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else "-"
        )

        def make_thumb(url):
            if url:
                return (
                    f'<div class="thumb-cell">'
                    f'<img src="{url}" class="thumb-img" loading="lazy" '
                    f'onerror="this.parentElement.innerHTML=\'<div class=\\\"thumb-placeholder\\\">📦</div>\'">'
                    f'</div>'
                )
            return '<div class="thumb-cell"><div class="thumb-placeholder">📦</div></div>'
        df_page["Foto"] = df_page["Thumbnail"].apply(make_thumb)

        def make_link(row):
            if row["Link"]:
                return f'<a href="{row["Link"]}" target="_blank" class="offer-link">🔗 Ver oferta</a>'
            return "–"
        df_page["Oferta"] = df_page.apply(make_link, axis=1)

        def loja_badge(loja):
            if not loja:
                return "–"
            cor = "#1f77b4"
            return f'<span class="store-badge">{loja}</span>'
        df_page["Loja_fmt"] = df_page["Loja"].apply(loja_badge)

        # ── Heading ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="section-heading">
            🛒 Resultados encontrados
            <span class="currency-note">💡 Preços em R$ — busca localizada para BR</span>
        </div>
        <div class="results-badge">✦ {total} produtos para "{st.session_state.last_query}"</div>
        """, unsafe_allow_html=True)

        # ── Table ─────────────────────────────────────────────────────────
        table_html = df_page.to_html(
            columns=["Foto", "Título", "Preço_fmt", "Loja_fmt", "Oferta"],
            escape=False,
            index=False,
            header=["", "Produto", "Preço", "Loja", "Oferta"]
        )
        st.write(
            f'<div class="product-table-wrapper">{table_html}</div>',
            unsafe_allow_html=True
        )

        # ── Pagination controls ───────────────────────────────────────────
        col_prev, col_info, col_next = st.columns([1, 3, 1])
        with col_prev:
            if st.button("← Anterior", disabled=(page == 0), key="btn_prev"):
                st.session_state.page -= 1
                st.rerun()
        with col_info:
            st.markdown(
                f'<div class="pagination-bar"><span class="page-info">Página {page + 1} de {total_pages} &nbsp;·&nbsp; mostrando {start + 1}–{min(end, total)} de {total}</span></div>',
                unsafe_allow_html=True
            )
        with col_next:
            if st.button("Próxima →", disabled=(page >= total_pages - 1), key="btn_next"):
                st.session_state.page += 1
                st.rerun()

        # ── Stat Cards ────────────────────────────────────────────────────
        menor = df["Preço"].min()
        maior = df["Preço"].max()
        media = df["Preço"].mean()

        st.markdown('<div class="section-heading">📈 Resumo de preços</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card min">
                <div class="stat-label">▼ Menor preço</div>
                <div class="stat-value">R$ {menor:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card avg">
                <div class="stat-label">◆ Média de preços</div>
                <div class="stat-value">R$ {media:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card max">
                <div class="stat-label">▲ Maior preço</div>
                <div class="stat-value">R$ {maior:,.2f}</div>
            </div>""", unsafe_allow_html=True)

        # ── Chart ─────────────────────────────────────────────────────────
        st.markdown('<div class="section-heading" style="margin-top:2.5rem">📊 Distribuição de preços por loja</div>', unsafe_allow_html=True)

        df_chart = df.copy()
        df_chart["Preço_fmt"] = df_chart["Preço"].apply(lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else "-")

        fig = px.bar(
            df_chart,
            x="Loja",
            y="Preço",
            color="Loja",
            text="Preço_fmt",
            title="Preços por Loja",
            labels={"Preço": "Preço (R$)", "Loja": "Loja"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            showlegend=False, height=450,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=12),
            title=dict(font=dict(family="Syne, sans-serif", color="#f1f5f9", size=18)),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickcolor="rgba(255,255,255,0.08)"),
            colorway=["#6366f1","#818cf8","#a78bfa","#ec4899","#f43f5e","#10b981","#0ea5e9","#f59e0b"],
            bargap=0.35,
        )
        st.plotly_chart(fig, use_container_width=True)