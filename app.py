# ================================================================
# app.py — Interface principal do Streamlit
# ================================================================

import streamlit as st
import requests as rq

st.set_page_config(page_title="Análise de Tickets e TMA", layout="wide")

# Menu lateral (sidebar)
st.sidebar.title("📁 Upload de Arquivo")
uploaded_file = st.sidebar.file_uploader("Escolha o arquivo CSV", type=["csv"])

st.title("📊 Análise de Tickets e Tempo Médio de Atendimento (TMA)")
st.markdown("Analise a relação entre o volume de tickets e o tempo médio de atendimento por agente.")

if uploaded_file:
    try:
        df = rq.load_data(uploaded_file)
        st.success("✅ Arquivo carregado com sucesso!")
        st.dataframe(df.head())

        resumo_geral, por_agente, fig_disp = rq.analyze_data(df)

        # Resumo geral
        st.subheader("📋 Resumo Geral")
        for k, v in resumo_geral.items():
            st.write(f"**{k}:** {v}")

        # Gráfico de dispersão
        st.subheader("📈 Relação Volume x Tempo Médio")
        st.plotly_chart(fig_disp, use_container_width=True)

        # Tabela detalhada
        st.subheader("📊 Desempenho por Agente")
        st.dataframe(por_agente[["agente_email", "qtd_tickets", "tma_formatado"]], use_container_width=True)

        # Insights automáticos via Groq
        st.subheader("💡 Insights (Gerados por IA via Groq API)")
        with st.spinner("Gerando insights inteligentes..."):
            insights = rq.generate_insights(df)
            st.write(insights)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Envie um arquivo CSV no menu lateral para iniciar a análise.")
