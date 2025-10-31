# ================================================================
# requests.py — funções de leitura, análise e integração com Groq
# ================================================================

import pandas as pd
import numpy as np
import plotly.express as px
import json
from groq import Groq


# ---------------------------------------------------------------
# Função: converter segundos em formato D:H:M:S
# ---------------------------------------------------------------
def format_seconds(total_seconds):
    total_seconds = int(total_seconds)
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


# ---------------------------------------------------------------
# Função: carregar dados do CSV
# ---------------------------------------------------------------
def load_data(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=None, engine="python", encoding="latin1")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo: {e}")

    df.columns = [c.strip().lower() for c in df.columns]
    return df


# ---------------------------------------------------------------
# Função: análise principal dos dados
# ---------------------------------------------------------------
def analyze_data(df):
    required_cols = {"agente_email", "qtd_motivos", "tma_segundos"}
    if not required_cols.issubset(df.columns):
        raise Exception(f"O arquivo deve conter as colunas: {', '.join(required_cols)}")

    df["qtd_motivos"] = pd.to_numeric(df["qtd_motivos"], errors="coerce").fillna(0)
    df["tma_segundos"] = pd.to_numeric(df["tma_segundos"], errors="coerce").fillna(0)

    # Estatísticas gerais
    resumo_geral = {
        "Total de agentes": df["agente_email"].nunique(),
        "Total de tickets": int(df["qtd_motivos"].sum()),
        "TMA médio geral": format_seconds(df["tma_segundos"].mean()),
        "TMA máximo": format_seconds(df["tma_segundos"].max()),
        "TMA mínimo": format_seconds(df["tma_segundos"].min()),
    }

    # Estatísticas por agente
    por_agente = (
        df.groupby("agente_email")
        .agg(
            qtd_tickets=("qtd_motivos", "sum"),
            tma_medio=("tma_segundos", "mean"),
        )
        .reset_index()
    )

    por_agente["tma_formatado"] = por_agente["tma_medio"].apply(format_seconds)

    # Gráfico de dispersão
    fig_disp = px.scatter(
        por_agente,
        x="qtd_tickets",
        y="tma_medio",
        hover_data=["agente_email"],
        color="tma_medio",
        color_continuous_scale="Viridis",
        title="Relação entre Volume de Tickets e Tempo Médio de Atendimento",
        labels={
            "qtd_tickets": "Quantidade de Tickets",
            "tma_medio": "Tempo Médio (segundos)",
        },
    )

    # Ordena para visualização
    por_agente = por_agente.sort_values(by="tma_medio", ascending=True)

    return resumo_geral, por_agente, fig_disp


# ---------------------------------------------------------------
# Função: gerar insights via API da Groq
# ---------------------------------------------------------------
def generate_insights(df):
    try:
        tickets_data = df.to_dict(orient="records")
        prompt = (

            f"Dados:\n{json.dumps(tickets_data, ensure_ascii=False)}"
        )

        client = Groq(api_key="")

        comple
