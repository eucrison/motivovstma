# ================================================================
# requests.py
# Módulo de leitura, limpeza, análise e visualização de dados
# ================================================================

import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------------
# Função para carregar o CSV com detecção automática
# ---------------------------------------------------------------
def load_data(uploaded_file):
    if uploaded_file is None:
        return None

    # Tenta detectar separador e encoding
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=None, engine="python", encoding="latin1")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo: {e}")

    # Normaliza nomes de colunas
    df.columns = [c.strip().lower() for c in df.columns]
    return df


# ---------------------------------------------------------------
# Função principal de análise
# ---------------------------------------------------------------
def analyze_data(df):
    # Confere colunas obrigatórias
    required_cols = {"agente_email", "qtd_motivos", "tempo_medio_atendimento"}
    if not required_cols.issubset(df.columns):
        raise Exception(f"O arquivo deve conter as colunas: {', '.join(required_cols)}")

    # Conversões e limpeza
    df["qtd_motivos"] = pd.to_numeric(df["qtd_motivos"], errors="coerce").fillna(0)
    df["tempo_medio_atendimento"] = pd.to_numeric(df["tempo_medio_atendimento"], errors="coerce").fillna(0)

    # Estatísticas gerais
    resumo_geral = {
        "Total de agentes": df["agente_email"].nunique(),
        "Total de tickets": int(df["qtd_motivos"].sum()),
        "Tempo médio geral": round(df["tempo_medio_atendimento"].mean(), 2),
        "Tempo máximo": round(df["tempo_medio_atendimento"].max(), 2),
        "Tempo mínimo": round(df["tempo_medio_atendimento"].min(), 2),
    }

    # Estatísticas por agente
    por_agente = (
        df.groupby("agente_email")
        .agg(
            qtd_tickets=("qtd_motivos", "sum"),
            tempo_medio=("tempo_medio_atendimento", "mean"),
        )
        .reset_index()
        .sort_values(by="tempo_medio", ascending=True)
    )

    # Gráficos (usando Plotly Express)
    fig_qtd = px.bar(
        por_agente,
        x="agente_email",
        y="qtd_tickets",
        title="Quantidade de Tickets por Agente",
        color="qtd_tickets",
        color_continuous_scale="Blues",
    )

    fig_tempo = px.bar(
        por_agente,
        x="agente_email",
        y="tempo_medio",
        title="Tempo Médio de Atendimento por Agente",
        color="tempo_medio",
        color_continuous_scale="Viridis",
    )

    # Tendências / insights
    media_geral = df["tempo_medio_atendimento"].mean()
    agentes_acima = por_agente[por_agente["tempo_medio"] > media_geral]
    agentes_abaixo = por_agente[por_agente["tempo_medio"] <= media_geral]

    insights = {
        "ponto_positivo": f"{len(agentes_abaixo)} agentes estão com tempo médio abaixo da média geral ({media_geral:.2f}).",
        "ponto_atencao": f"{len(agentes_acima)} agentes estão com tempo médio acima da média geral ({media_geral:.2f}).",
        "melhor_agente": por_agente.iloc[0]["agente_email"],
        "pior_agente": por_agente.iloc[-1]["agente_email"],
    }

    return resumo_geral, por_agente, fig_qtd, fig_tempo, insights

