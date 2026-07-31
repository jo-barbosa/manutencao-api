import os
from typing import Dict, List, Any, Optional
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")


def get_headers() -> Dict[str, str]:
    """Retorna o cabeçalho HTTP com o Token JWT de autorização."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def login(email: str, password: str) -> Dict[str, Any]:
    response = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()
    raise ValueError("Credenciais inválidas ou erro na autenticação.")


def get_me() -> Optional[Dict[str, Any]]:
    response = requests.get(f"{API_URL}/auth/me", headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None


def get_fabricas() -> List[Dict[str, Any]]:
    res = requests.get(f"{API_URL}/fabricas", headers=get_headers())
    return res.json() if res.status_code == 200 else []


def get_linhas(fabrica_id: Optional[int] = None) -> List[Dict[str, Any]]:
    if fabrica_id:
        res = requests.get(f"{API_URL}/fabricas/{fabrica_id}/linhas", headers=get_headers())
    else:
        # Se não especificou fábrica, procura todas as fábricas e agrega as linhas
        fabricas = get_fabricas()
        todas_linhas = []
        for f in fabricas:
            res = requests.get(f"{API_URL}/fabricas/{f['id']}/linhas", headers=get_headers())
            if res.status_code == 200:
                todas_linhas.extend(res.json())
        return todas_linhas
    return res.json() if res.status_code == 200 else []


def get_sistemas(linha_id: Optional[int] = None) -> List[Dict[str, Any]]:
    if linha_id:
        res = requests.get(f"{API_URL}/linhas/{linha_id}/sistemas", headers=get_headers())
        return res.json() if res.status_code == 200 else []
    res = requests.get(f"{API_URL}/sistemas", headers=get_headers())
    return res.json() if res.status_code == 200 else []


def get_sistemas_status() -> List[Dict[str, Any]]:
    res = requests.get(f"{API_URL}/sistemas/status", headers=get_headers())
    return res.json() if res.status_code == 200 else []


def get_fornecedores() -> List[Dict[str, Any]]:
    res = requests.get(f"{API_URL}/fornecedores", headers=get_headers())
    return res.json() if res.status_code == 200 else []


def get_superusers() -> List[Dict[str, Any]]:
    res = requests.get(f"{API_URL}/superusers", headers=get_headers())
    return res.json() if res.status_code == 200 else []


def get_acoes() -> List[Dict[str, Any]]:
    res = requests.get(f"{API_URL}/acoes", headers=get_headers())
    return res.json() if res.status_code == 200 else []


def criar_acao(payload: Dict[str, Any]) -> requests.Response:
    return requests.post(f"{API_URL}/acoes", json=payload, headers=get_headers())


def fechar_acao(acao_id: int, data_conclusao: Optional[str] = None, comentario: Optional[str] = None) -> requests.Response:
    payload = {}
    if data_conclusao:
        payload["data_conclusao"] = data_conclusao
    if comentario:
        payload["comentario"] = comentario
    return requests.put(f"{API_URL}/acoes/{acao_id}/fechar", json=payload, headers=get_headers())


def editar_acao(acao_id: int, payload: Dict[str, Any]) -> requests.Response:
    return requests.put(f"{API_URL}/acoes/{acao_id}", json=payload, headers=get_headers())


def criar_sistema(payload: Dict[str, Any]) -> requests.Response:
    return requests.post(f"{API_URL}/sistemas", json=payload, headers=get_headers())


def criar_fornecedor(payload: Dict[str, Any]) -> requests.Response:
    return requests.post(f"{API_URL}/fornecedores", json=payload, headers=get_headers())


def editar_fornecedor(fornecedor_id: int, payload: Dict[str, Any]) -> requests.Response:
    return requests.put(f"{API_URL}/fornecedores/{fornecedor_id}", json=payload, headers=get_headers())


def get_pds_geral() -> Optional[str]:
    res = requests.get(f"{API_URL}/pds/geral", headers=get_headers())
    if res.status_code == 200:
        return res.json().get("pds")
    return None


def get_pds_operador(superuser_id: int) -> Optional[str]:
    res = requests.get(f"{API_URL}/pds/operador/{superuser_id}", headers=get_headers())
    if res.status_code == 200:
        return res.json().get("pds")
    return None


def get_auditoria() -> List[Dict[str, Any]]:
    res = requests.get(f"{API_URL}/auditoria", headers=get_headers())
    return res.json() if res.status_code == 200 else []