# ================================================================
# app.py
# Interface Streamlit para análise de tickets e desempenho de agentes
# ================================================================

import streamlit as st
import requests as rq

st.set_page_config(page_title="Análise de Tickets", layout="wide")

st.title("📊 Análise de Tickets e Desempenho de Agentes")
st.markdown("Envie um arquivo `.csv` com as colunas **agente_email**, **qtd_motivos** e **tma_segundos**.")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha o arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = rq.load_data(uploaded_file)

        st.success("✅ Arquivo carregado com sucesso!")
        st.dataframe(df.head())

        resumo_geral, por_agente, fig_qtd, fig_tempo, insights = rq.analyze_data(df)

        # Exibe resumo geral
        st.subheader("📋 Resumo Geral")
        for k, v in resumo_geral.items():
            st.write(f"**{k}:** {v}")

        # Exibe gráficos
        st.subheader("📈 Quantidade de Tickets por Agente")
        st.plotly_chart(fig_qtd, use_container_width=True)

        st.subheader("⏱️ Tempo Médio de Atendimento por Agente")
        st.plotly_chart(fig_tempo, use_container_width=True)

        # Exibe tabela detalhada
        st.subheader("📊 Desempenho por Agente")
        st.dataframe(por_agente, use_container_width=True)

        # Exibe insights
        st.subheader("💡 Insights")
        st.info(insights["ponto_positivo"])
        st.warning(insights["ponto_atencao"])
        st.success(f"🏅 Melhor desempenho: {insights['melhor_agente']}")
        st.error(f"⚠️ Maior tempo médio: {insights['pior_agente']}")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo CSV para iniciar a análise.")

