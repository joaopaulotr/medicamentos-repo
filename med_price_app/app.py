"""
app.py
Interface principal do Sistema de Comparação de Preços de Medicamentos
usando Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

# Adiciona o diretório atual ao path para importar módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import MEDICAMENTOS, buscar_precos_medicamento
from utils import (
    calcular_media_precos,
    menor_preco,
    maior_preco,
    criar_dataframe_precos,
    gerar_estatisticas,
    formatar_moeda,
    calcular_economia,
    calcular_percentual_diferenca
)


# Configuração da página
st.set_page_config(
    page_title="Comparador de Preços de Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS customizado para melhorar a aparência
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .best-price {
        background-color: #1a3d2b;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #28a745;
        color: #e6f4ea;
    }
    .best-price h3, .best-price h2, .best-price p { color: #e6f4ea !important; }
    .worst-price {
        background-color: #3d1a1a;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #dc3545;
        color: #fde8e8;
    }
    .worst-price h3, .worst-price h2, .worst-price p { color: #fde8e8 !important; }
    </style>
""", unsafe_allow_html=True)


def exibir_header():
    """Exibe o cabeçalho da aplicação"""
    st.markdown('<h1 class="main-header">💊 Comparador de Preços de Medicamentos</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Encontre o melhor preço para seus medicamentos em diferentes farmácias</p>', unsafe_allow_html=True)
    st.markdown("---")


def exibir_sidebar():
    """Configura e exibe a barra lateral"""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/pharmacy-shop.png", width=80)
        st.title("ℹ️ Sobre")
        st.info(
            """
            Este sistema busca automaticamente os preços de medicamentos 
            em diferentes farmácias online e apresenta:
            
            - 📊 Comparação de preços
            - 📈 Análise estatística
            - 💰 Economia potencial
            - 📉 Gráficos interativos
            """
        )
        
        st.markdown("---")
        st.markdown("### 🕐 Última atualização")
        st.text(datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        st.markdown("---")
        st.markdown("### ⚙️ Configurações")
        st.caption("Versão 1.0.0")
        st.caption("Desenvolvido com ❤️ e Python")


@st.cache_data(ttl=3600)  # Cache por 1 hora
def buscar_precos_cached(medicamento):
    """
    Busca preços com cache para evitar scraping desnecessário.
    O cache expira após 1 hora (3600 segundos).
    
    Args:
        medicamento (str): Nome do medicamento
        
    Returns:
        list: Lista de preços encontrados
    """
    return buscar_precos_medicamento(medicamento)


def exibir_tabela_precos(resultados):
    """
    Exibe a tabela de preços formatada.
    
    Args:
        resultados (list): Lista de dicionários com preços
    """
    st.subheader("📋 Tabela Comparativa de Preços")
    
    df = criar_dataframe_precos(resultados)
    
    if not df.empty:
        # Renomeia colunas para exibição
        df_display = df.copy()
        df_display.columns = ['Farmácia', 'Preço', 'Produto', 'URL']
        
        # Remove a coluna URL da exibição mas mantém como link
        df_display = df_display[['Farmácia', 'Preço', 'Produto']]
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhum dado disponível para exibir.")


def exibir_estatisticas(stats):
    """
    Exibe as estatísticas dos preços em colunas.
    
    Args:
        stats (dict): Dicionário com estatísticas
    """
    st.subheader("📊 Estatísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if stats['media']:
            st.metric(
                label="💵 Preço Médio",
                value=formatar_moeda(stats['media'])
            )
        else:
            st.metric(label="💵 Preço Médio", value="N/A")
    
    with col2:
        if stats['menor']:
            st.metric(
                label="✅ Menor Preço",
                value=formatar_moeda(stats['menor']['preco']),
                delta=f"{stats['menor']['farmacia']}"
            )
        else:
            st.metric(label="✅ Menor Preço", value="N/A")
    
    with col3:
        if stats['maior']:
            st.metric(
                label="❌ Maior Preço",
                value=formatar_moeda(stats['maior']['preco']),
                delta=f"{stats['maior']['farmacia']}"
            )
        else:
            st.metric(label="❌ Maior Preço", value="N/A")
    
    with col4:
        if stats['economia']:
            st.metric(
                label="💰 Economia",
                value=formatar_moeda(stats['economia']),
                delta=f"-{stats['diferenca_percentual']:.1f}%" if stats['diferenca_percentual'] else ""
            )
        else:
            st.metric(label="💰 Economia", value="N/A")


def exibir_destaques(stats):
    """
    Exibe cards destacando o melhor e pior preço.
    
    Args:
        stats (dict): Dicionário com estatísticas
    """
    if stats['menor'] and stats['maior']:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                f"""
                <div class="best-price">
                    <h3>🏆 Melhor Oferta</h3>
                    <p><strong>{stats['menor']['farmacia']}</strong></p>
                    <h2>{formatar_moeda(stats['menor']['preco'])}</h2>
                    <p><a href="{stats['menor']['url']}" target="_blank">Ver na loja →</a></p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="worst-price">
                    <h3>⚠️ Preço Mais Alto</h3>
                    <p><strong>{stats['maior']['farmacia']}</strong></p>
                    <h2>{formatar_moeda(stats['maior']['preco'])}</h2>
                    <p><a href="{stats['maior']['url']}" target="_blank">Ver na loja →</a></p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Alerta de economia
        if stats['economia'] and stats['economia'] > 0:
            st.success(
                f"💡 Você pode economizar até **{formatar_moeda(stats['economia'])}** "
                f"({stats['diferenca_percentual']:.1f}%) comprando na farmácia mais barata!"
            )


def exibir_grafico(resultados):
    """
    Exibe gráfico de barras comparativo dos preços.
    
    Args:
        resultados (list): Lista de dicionários com preços
    """
    st.subheader("📈 Gráfico Comparativo")
    
    if not resultados:
        st.warning("Sem dados para exibir no gráfico.")
        return
    
    # Prepara dados para o gráfico
    df = pd.DataFrame(resultados)
    
    # Cria gráfico de barras com Plotly
    fig = px.bar(
        df,
        x='farmacia',
        y='preco',
        title='Comparação de Preços por Farmácia',
        labels={'farmacia': 'Farmácia', 'preco': 'Preço (R$)'},
        color='preco',
        color_continuous_scale='RdYlGn_r',  # Vermelho (alto) para Verde (baixo)
        text='preco'
    )
    
    # Formata os valores no gráfico
    fig.update_traces(
        texttemplate='R$ %{text:.2f}',
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_title="Farmácia",
        yaxis_title="Preço (R$)",
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Função principal da aplicação"""
    
    # Exibe header e sidebar
    exibir_header()
    exibir_sidebar()
    
    # Seção de seleção de medicamento
    st.subheader("🔍 Selecione um Medicamento")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Selectbox com medicamentos disponíveis
        medicamento_selecionado = st.selectbox(
            "Escolha o medicamento:",
            options=list(MEDICAMENTOS.keys()),
            index=0
        )
        
        # Exibe informações do medicamento
        if medicamento_selecionado:
            info = MEDICAMENTOS[medicamento_selecionado]
            st.caption(f"**Fabricante:** {info['fabricante']}")
    
    with col2:
        st.write("")  # Espaçamento
        st.write("")  # Espaçamento
        buscar_button = st.button("🔎 Buscar Preços", type="primary", use_container_width=True)
    
    # Linha divisória
    st.markdown("---")
    
    # Inicializa session_state
    if 'resultados' not in st.session_state:
        st.session_state.resultados = None
    if 'forcar_busca' not in st.session_state:
        st.session_state.forcar_busca = False


    # Botão para atualizar preços (limpa cache e força busca nova)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Atualizar Preços", use_container_width=True):
            st.cache_data.clear()
            st.session_state.forcar_busca = True
            st.session_state.resultados = None
            st.rerun()

    # Quando o botão Buscar é clicado OU flag de forçar busca está ativa
    if buscar_button or st.session_state.forcar_busca:
        if medicamento_selecionado:
            with st.spinner(f"🔍 Buscando preços de **{medicamento_selecionado}**... Isso pode levar alguns segundos."):
                st.session_state.resultados = buscar_precos_cached(medicamento_selecionado)
                st.session_state.forcar_busca = False
        else:
            st.warning("⚠️ Por favor, selecione um medicamento.")

    resultados = st.session_state.resultados
    if resultados:
        st.success(f"✅ Encontrados {len(resultados)} preço(s)!")
        # Gera estatísticas
        stats = gerar_estatisticas(resultados)
        # Exibe destaques
        exibir_destaques(stats)
        st.markdown("---")
        # Exibe estatísticas
        exibir_estatisticas(stats)
        st.markdown("---")
        # Exibe tabela
        exibir_tabela_precos(resultados)
        st.markdown("---")
        # Exibe gráfico
        exibir_grafico(resultados)
    elif buscar_button or st.session_state.forcar_busca:
        st.error(
            "❌ Não foi possível encontrar preços no momento. "
            "Isso pode ocorrer por:\n"
            "- Sites temporariamente indisponíveis\n"
            "- Mudanças na estrutura das páginas\n"
            "- Problemas de conexão\n\n"
            "Tente novamente em alguns instantes."
        )
    
    # Informações adicionais no rodapé
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p><strong>⚠️ Aviso Importante:</strong></p>
            <p>Os preços são coletados automaticamente e podem variar. 
            Sempre confirme o valor final no site da farmácia antes da compra.</p>
            <p style='margin-top: 1rem;'>Desenvolvido com Streamlit | Python | Selenium</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
