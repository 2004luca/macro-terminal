# utils/fetchers.py
# Responsabilidade: centralizar todas as buscas de dados externos.
# Nenhuma página deve buscar dados diretamente — sempre via esse arquivo.

import pandas as pd
from fredapi import Fred
import streamlit as st


def get_fred_client():
    """
    Cria e retorna a conexão com a API do FRED.
    A chave é lida do secrets.toml — nunca escrita direto no código.
    """
    return Fred(api_key=st.secrets["FRED_API_KEY"])


def get_series(series_id: str, start_date: str = "2000-01-01") -> pd.Series:
    """
    Busca uma série histórica do FRED pelo ID.

    Parâmetros:
        series_id  → o código da série. Ex: "FEDFUNDS" = juros dos EUA
        start_date → de quando você quer os dados. Padrão: ano 2000

    Retorna:
        pd.Series → uma coluna de dados indexada por data
    """
    fred = get_fred_client()
    data = fred.get_series(series_id, observation_start=start_date)
    return data