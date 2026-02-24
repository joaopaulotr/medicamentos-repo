from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Pesquise Mais", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, .stTextInput, .stButton, p, span, div, td, th, a {
    font-family: 'Open Sans', sans-serif !important;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 80% 80%, rgba(236,72,153,0.10) 0%, transparent 50%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1400px; }

/* ── Hero ── */
.hero-header { text-align: center; padding: 3rem 0 2rem; }
.hero-tag {
    display: inline-block; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.22em;
    text-transform: uppercase; color: #818cf8; background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25); padding: 0.32rem 1rem;
    border-radius: 100px; margin-bottom: 1.1rem;
}
.hero-title {
    font-family: 'Open Sans', sans-serif !important; font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -0.02em; color: #f8fafc; margin: 0 0 0.7rem;
}
.hero-title span {
    background: linear-gradient(135deg, #818cf8 0%, #ec4899 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { font-size: 1rem; color: #94a3b8; font-weight: 300; margin: 0; }

/* ── Search area ── */
.search-wrap {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px; padding: 1.6rem 2rem 1.4rem; margin: 1.5rem 0 0.4rem;
}

/* Input */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important; color: #f1f5f9 !important;
    font-family: 'Open Sans', sans-serif !important; font-size: 0.95rem !important;
    padding: 0.65rem 1rem !important; transition: all 0.2s ease !important; height: 44px !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    background: rgba(99,102,241,0.07) !important;
}
.stTextInput > div > div > input::placeholder { color: #475569 !important; }
.stTextInput label {
    color: #94a3b8 !important; font-size: 0.72rem !important; font-weight: 600 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    font-family: 'Open Sans', sans-serif !important; margin-bottom: 6px !important;
}
div[data-testid="stTextInput"] { margin-bottom: 0 !important; }

/* Button — same height as input */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important; font-family: 'Open Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 0.88rem !important; letter-spacing: 0.04em !important; border: none !important;
    border-radius: 10px !important; padding: 0 1.5rem !important; width: 100% !important;
    height: 44px !important; min-height: 44px !important; max-height: 44px !important;
    line-height: 44px !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.35) !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 26px rgba(99,102,241,0.5) !important;
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.stCaption { color: #3f4858 !important; font-size: 0.72rem !important; }

/* ── Section heading ── */
.section-heading {
    font-family: 'Open Sans', sans-serif !important; font-size: 1.15rem; font-weight: 700;
    color: #f1f5f9; letter-spacing: -0.01em; margin: 2rem 0 0.9rem;
    display: flex; align-items: center; gap: 0.55rem;
}
.section-heading::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.4), transparent);
}

.results-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-size: 0.73rem; font-weight: 600; color: #818cf8;
    background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2);
    padding: 0.26rem 0.75rem; border-radius: 100px; letter-spacing: 0.03em; margin-bottom: 0.9rem;
}

/* ── Table ── */
.product-table-wrapper {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; overflow: hidden; margin-bottom: 1rem;
}
.product-table-wrapper table { width: 100%; border-collapse: collapse; }
.product-table-wrapper thead tr {
    background: rgba(99,102,241,0.1); border-bottom: 1px solid rgba(99,102,241,0.2);
}
.product-table-wrapper thead th {
    padding: 0.8rem 1rem; text-align: left; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase; color: #818cf8;
    font-family: 'Open Sans', sans-serif;
}
.product-table-wrapper thead th:first-child { width: 90px; text-align: center; }
.product-table-wrapper tbody tr { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
.product-table-wrapper tbody tr:hover { background: rgba(255,255,255,0.04); }
.product-table-wrapper tbody tr:last-child { border-bottom: none; }
.product-table-wrapper tbody td {
    padding: 0.7rem 1rem; font-size: 0.86rem; color: #cbd5e1; vertical-align: middle;
    font-family: 'Open Sans', sans-serif;
}
.product-table-wrapper tbody td:nth-child(2) {
    color: #f1f5f9; max-width: 300px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.product-table-wrapper tbody td:nth-child(3) {
    font-weight: 700; color: #a5b4fc; white-space: nowrap;
}
/* highlight menor/maior preço */
.price-min { color: #34d399 !important; }
.price-max { color: #f472b6 !important; }

/* Thumbnail */
.thumb-cell { text-align: center; padding: 0.5rem 0.6rem !important; }
.thumb-img {
    width: 72px; height: 72px; object-fit: contain; border-radius: 10px;
    background: rgba(255,255,255,0.08); padding: 6px;
    border: 1px solid rgba(255,255,255,0.1); display: block; margin: 0 auto;
    transition: transform 0.2s ease;
}
.thumb-img:hover { transform: scale(1.12); cursor: zoom-in; }
.thumb-placeholder {
    width: 72px; height: 72px; border-radius: 10px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto; font-size: 1.6rem;
}

/* Store badge */
.store-badge {
    display: inline-block; font-size: 0.73rem; font-weight: 600; color: #94a3b8;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09);
    padding: 0.18rem 0.55rem; border-radius: 6px; white-space: nowrap;
}

/* Links */
a.offer-link {
    display: inline-flex; align-items: center; gap: 0.25em; font-size: 0.75rem; font-weight: 600;
    color: #818cf8; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.22);
    padding: 0.2rem 0.6rem; border-radius: 6px; text-decoration: none;
    transition: all 0.15s; white-space: nowrap;
}
a.offer-link:hover { background: rgba(99,102,241,0.22); color: #a5b4fc; }
a.product-link {
    display: inline-flex; align-items: center; gap: 0.25em; font-size: 0.75rem; font-weight: 600;
    color: #6ee7b7; background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2);
    padding: 0.2rem 0.6rem; border-radius: 6px; text-decoration: none;
    transition: all 0.15s; white-space: nowrap; margin-left: 4px;
}
a.product-link:hover { background: rgba(16,185,129,0.18); color: #a7f3d0; }

/* Links cell — stack them */
.links-cell { display: flex; flex-direction: column; gap: 5px; align-items: flex-start; }

/* ── Pagination ── */
.pag-info {
    text-align: center; font-size: 0.75rem; color: #4b5563;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    padding: 0.4rem 1rem; border-radius: 8px; margin: 0 auto; width: fit-content;
    margin-bottom: 0.5rem;
}

/* Stat cards */
.stats-row { display: flex; gap: 1rem; margin-bottom: 2rem; }
.stat-card {
    flex: 1; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 1.3rem 1.5rem; text-align: center;
    position: relative; overflow: hidden; transition: transform 0.2s, border-color 0.2s;
}
.stat-card:hover { transform: translateY(-3px); border-color: rgba(99,102,241,0.3); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.stat-card.smin::before { background: linear-gradient(90deg, #10b981, #34d399); }
.stat-card.savg::before { background: linear-gradient(90deg, #6366f1, #818cf8); }
.stat-card.smax::before { background: linear-gradient(90deg, #ec4899, #f43f5e); }
.stat-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #64748b; margin-bottom: 0.4rem; }
.stat-name { font-size: 0.7rem; color: #475569; margin-top: 0.35rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-value { font-family: 'Open Sans', sans-serif; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1; }
.stat-card.smin .stat-value { color: #34d399; }
.stat-card.savg .stat-value { color: #818cf8; }
.stat-card.smax .stat-value { color: #f472b6; }

.currency-note {
    font-size: 0.68rem; color: #3f4858; background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05); padding: 0.18rem 0.6rem;
    border-radius: 6px; margin-left: 0.4rem; font-weight: 400;
}
.stSpinner > div { border-top-color: #6366f1 !important; }
.js-plotly-plot .plotly, .plot-container { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-tag">⚡ Powered by Pesquise Mais · Google Shopping</div>
    <h1 class="hero-title">Busca <span>Inteligente</span><br>de Produtos</h1>
    <p class="hero-sub">Compare preços em tempo real e encontre as melhores ofertas</p>
</div>
""", unsafe_allow_html=True)

# ── Search ────────────────────────────────────────────────────────────────────
st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    q = st.text_input("O que você quer buscar?", value="notebook")
with col_btn:
    # label spacer so button aligns with input field (same label height)
    st.markdown("<p style='font-size:0.72rem;color:transparent;margin-bottom:6px;line-height:1.2'>&nbsp;</p>", unsafe_allow_html=True)
    search_clicked = st.button("🔍 Buscar")
location = "Sao Paulo, State of Sao Paulo, brazil"
st.caption(f"📍 Localização fixa: {location}")
st.markdown('</div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
ROWS_PER_PAGE = 5

if "df_results" not in st.session_state:
    st.session_state.df_results = None
if "page" not in st.session_state:
    st.session_state.page = 0
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# ── API call ──────────────────────────────────────────────────────────────────
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
                            "ProductLink": p.get("product_link", ""),
                            "Thumbnail": p.get("thumbnail", ""),
                        }
                        for p in produtos if p.get("price")
                    ])
                    st.session_state.df_results = df
                    st.session_state.page = 0
                    st.session_state.last_query = q
            else:
                st.error(f"Erro na consulta: {resp.status_code}")

    # ── Render results ────────────────────────────────────────────────────────
    if st.session_state.df_results is not None:
        df = st.session_state.df_results
        total = len(df)
        total_pages = max(1, -(-total // ROWS_PER_PAGE))
        page = st.session_state.page

        start = page * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        df_page = df.iloc[start:end].copy()

        # Global min/max for highlighting
        global_min = df["Preço"].min()
        global_max = df["Preço"].max()
        min_title = df.loc[df["Preço"].idxmin(), "Título"]
        max_title = df.loc[df["Preço"].idxmax(), "Título"]
        min_loja  = df.loc[df["Preço"].idxmin(), "Loja"]
        max_loja  = df.loc[df["Preço"].idxmax(), "Loja"]

        # ── Stat Cards (always full dataset) ─────────────────────────────
        st.markdown('<div class="section-heading">📈 Resumo de preços</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card smin">
                <div class="stat-label">▼ Menor preço</div>
                <div class="stat-value">R$ {global_min:,.2f}</div>
                <div class="stat-name">🏪 {min_loja or '—'}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            media = df["Preço"].mean()
            st.markdown(f"""
            <div class="stat-card savg">
                <div class="stat-label">◆ Média geral</div>
                <div class="stat-value">R$ {media:,.2f}</div>
                <div class="stat-name">{total} produtos encontrados</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card smax">
                <div class="stat-label">▲ Maior preço</div>
                <div class="stat-value">R$ {global_max:,.2f}</div>
                <div class="stat-name">🏪 {max_loja or '—'}</div>
            </div>""", unsafe_allow_html=True)

        # ── Table ─────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="section-heading">
            🛒 Resultados
            <span class="currency-note">💡 Preços em R$ — busca localizada BR</span>
        </div>
        <div class="results-badge">✦ {total} produtos para "{st.session_state.last_query}" · página {page+1}/{total_pages}</div>
        """, unsafe_allow_html=True)

        def make_thumb(url):
            if url:
                return (
                    f'<div class="thumb-cell">'
                    f'<img src="{url}" class="thumb-img" loading="lazy" '
                    f'onerror="this.parentElement.innerHTML=\'<div class=\\\"thumb-placeholder\\\">📦</div>\'">'
                    f'</div>'
                )
            return '<div class="thumb-cell"><div class="thumb-placeholder">📦</div></div>'

        def make_price_cell(row):
            val = row["Preço"]
            if pd.isnull(val):
                return "–"
            fmt = f"R$ {val:,.2f}"
            if val == global_min:
                return f'<span class="price-min">▼ {fmt}</span>'
            if val == global_max:
                return f'<span class="price-max">▲ {fmt}</span>'
            return fmt

        def make_links(row):
            parts = []
            if row.get("Link"):
                parts.append(f'<a href="{row["Link"]}" target="_blank" class="offer-link">🔗 Ver oferta</a>')
            if row.get("ProductLink"):
                parts.append(f'<a href="{row["ProductLink"]}" target="_blank" class="product-link">🛒 Produto</a>')
            return f'<div class="links-cell">{"".join(parts)}</div>' if parts else "–"

        def loja_badge(loja):
            return f'<span class="store-badge">{loja}</span>' if loja else "–"

        df_page["Foto"]      = df_page["Thumbnail"].apply(make_thumb)
        df_page["Preço_fmt"] = df_page.apply(make_price_cell, axis=1)
        df_page["Loja_fmt"]  = df_page["Loja"].apply(loja_badge)
        df_page["Links"]     = df_page.apply(make_links, axis=1)

        table_html = df_page.to_html(
            columns=["Foto", "Título", "Preço_fmt", "Loja_fmt", "Links"],
            escape=False, index=False,
            header=["", "Produto", "Preço", "Loja", "Links"]
        )
        st.write(f'<div class="product-table-wrapper">{table_html}</div>', unsafe_allow_html=True)

        # ── Pagination ────────────────────────────────────────────────────
        col_prev, col_info, col_next = st.columns([1, 3, 1])
        with col_prev:
            if st.button("← Anterior", disabled=(page == 0), key="btn_prev"):
                st.session_state.page -= 1
                st.rerun()
        with col_info:
            st.markdown(
                f'<div class="pag-info">Página {page+1} de {total_pages} &nbsp;·&nbsp; itens {start+1}–{min(end,total)} de {total}</div>',
                unsafe_allow_html=True
            )
        with col_next:
            if st.button("Próxima →", disabled=(page >= total_pages - 1), key="btn_next"):
                st.session_state.page += 1
                st.rerun()

        # ── Chart ─────────────────────────────────────────────────────────
        st.markdown('<div class="section-heading" style="margin-top:2rem">📊 Distribuição de preços por loja</div>', unsafe_allow_html=True)
        df_chart = df.copy()
        df_chart["Preço_fmt"] = df_chart["Preço"].apply(lambda x: f"R$ {x:,.2f}" if pd.notnull(x) else "–")
        fig = px.bar(
            df_chart, x="Loja", y="Preço", color="Loja", text="Preço_fmt",
            title="Preços por Loja", labels={"Preço": "Preço (R$)", "Loja": "Loja"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            showlegend=False, height=440,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Open Sans, sans-serif", color="#94a3b8", size=12),
            title=dict(font=dict(family="Open Sans, sans-serif", color="#f1f5f9", size=17)),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickcolor="rgba(255,255,255,0.08)"),
            colorway=["#6366f1","#818cf8","#a78bfa","#ec4899","#f43f5e","#10b981","#0ea5e9","#f59e0b"],
            bargap=0.35,
        )
        st.plotly_chart(fig, use_container_width=True)