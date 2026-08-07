from typing import Any

import requests
import streamlit as st


BASE_URL = "https://api.mobileapi.dev"

class MobileAPIError(Exception):
    """Erro controlado durante uma consulta à MobileAPI."""


def buscar_dispositivo(nome: str) -> dict[str, Any]:
    nome = nome.strip()

    if not nome:
        raise ValueError("O nome do equipamento não pode estar vazio.")

    try:
        api_key = st.secrets["MOBILE_API_KEY"]
    except KeyError as exc:
        raise MobileAPIError(
            "A chave MOBILE_API_KEY não foi encontrada."
        ) from exc

    url = f"{BASE_URL}/devices/search"

    headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json",
}

    parametros = {
        "name": nome,
    }

    try:
        resposta = requests.get(
            url,
            headers=headers,
            params=parametros,
            timeout=15,
        )
    except requests.Timeout as exc:
        raise MobileAPIError(
            "A consulta excedeu o tempo limite."
        ) from exc
    except requests.RequestException as exc:
        raise MobileAPIError(
            "Não foi possível conectar à API."
        ) from exc

    if resposta.status_code == 401:
        raise MobileAPIError("A chave da API é inválida.")

    if resposta.status_code == 403:
        raise MobileAPIError("O acesso à API foi negado.")

    if resposta.status_code == 404:
        return {
            "encontrado": False,
            "resultados": [],
        }

    if resposta.status_code == 429:
        raise MobileAPIError(
            "O limite de consultas da API foi atingido."
        )

    if not resposta.ok:
        raise MobileAPIError(
            f"A API retornou o código {resposta.status_code}."
        )

    return {
        "encontrado": True,
        "resultados": resposta.json(),
    }
