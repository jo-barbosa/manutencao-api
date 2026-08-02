import os
from typing import Dict, List, Any, Optional
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GRAPHQL_URL = os.getenv("GRAPHQL_URL", "http://127.0.0.1:8000/graphql")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

class DummyResponse:
    def __init__(self, status_code: int, text: str = "", json_data: dict = None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

def get_headers() -> Dict[str, str]:
    """Retorna o cabeçalho HTTP com o Token JWT de autorização."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def execute_graphql(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Executa uma query/mutação GraphQL no GraphQL Gateway."""
    payload = {"query": query, "variables": variables or {}}
    res = requests.post(GRAPHQL_URL, json=payload, headers=get_headers(), timeout=10)
    if res.status_code == 200:
        data = res.json()
        if "errors" in data:
            raise ValueError(data["errors"][0].get("message", "Erro em instrução GraphQL"))
        return data.get("data", {})
    raise ValueError(f"Erro no Gateway GraphQL ({res.status_code}): {res.text}")

def login(email: str, password: str) -> Dict[str, Any]:
    query = """
    mutation Login($email: String!, $password: String!) {
        login(email: $email, password: $password) {
            accessToken
            user {
                id
                nome
                email
            }
        }
    }
    """
    data = execute_graphql(query, {"email": email, "password": password})
    login_res = data.get("login")
    if login_res and login_res.get("accessToken"):
        return {
            "access_token": login_res["accessToken"],
            "token_type": "bearer",
            "user": login_res["user"]
        }
    raise ValueError("Credenciais inválidas ou erro na autenticação.")

def get_me() -> Optional[Dict[str, Any]]:
    token = st.session_state.get("token")
    if not token:
        return None
    query = """
    query Me($token: String!) {
        me(token: $token) {
            id
            nome
            email
        }
    }
    """
    try:
        data = execute_graphql(query, {"token": token})
        return data.get("me")
    except Exception:
        return None

def get_fabricas() -> List[Dict[str, Any]]:
    query = """
    query {
        fabricas {
            id
            nome
            localizacao
        }
    }
    """
    try:
        data = execute_graphql(query)
        return data.get("fabricas", [])
    except Exception:
        return []

def get_linhas(fabrica_id: Optional[int] = None) -> List[Dict[str, Any]]:
    query = """
    query GetLinhas($fabricaId: Int) {
        linhas(fabricaId: $fabricaId) {
            id
            nome
            fabricaId
        }
    }
    """
    try:
        data = execute_graphql(query, {"fabricaId": fabrica_id})
        return data.get("linhas", [])
    except Exception:
        return []

def get_sistemas(linha_id: Optional[int] = None) -> List[Dict[str, Any]]:
    query = """
    query GetSistemas($linhaId: Int) {
        sistemas(linhaId: $linhaId) {
            id
            nome
            estadoAtual
            linhaId
            fornecedorId
        }
    }
    """
    try:
        data = execute_graphql(query, {"linhaId": linha_id})
        res = []
        for s in data.get("sistemas", []):
            res.append({
                "id": s["id"],
                "nome": s["nome"],
                "estado_atual": s["estadoAtual"],
                "linha_id": s.get("linhaId"),
                "fornecedor_id": s.get("fornecedorId")
            })
        return res
    except Exception:
        return []

def get_sistemas_status() -> List[Dict[str, Any]]:
    query = """
    query {
        sistemasStatus {
            id
            nomeSistema
            estado
            linha
            fabrica
            fornecedor
        }
    }
    """
    try:
        data = execute_graphql(query)
        res = []
        for s in data.get("sistemasStatus", []):
            res.append({
                "id": s["id"],
                "nome_sistema": s["nomeSistema"],
                "estado": s["estado"],
                "linha": s["linha"],
                "fabrica": s["fabrica"],
                "fornecedor": s["fornecedor"]
            })
        return res
    except Exception:
        return []

def get_fornecedores() -> List[Dict[str, Any]]:
    query = """
    query {
        fornecedores {
            id
            nome
            contacto
        }
    }
    """
    try:
        data = execute_graphql(query)
        return data.get("fornecedores", [])
    except Exception:
        return []

def get_superusers() -> List[Dict[str, Any]]:
    query = """
    query {
        superusers {
            id
            nome
            email
        }
    }
    """
    try:
        data = execute_graphql(query)
        return data.get("superusers", [])
    except Exception:
        return []

def get_acoes() -> List[Dict[str, Any]]:
    query = """
    query {
        acoes {
            id
            descricao
            status
            impacto
            dataCriacao
            dataPrevistaConclusao
            dataConclusao
            comentarioFecho
            sistemaId
            responsavelId
        }
    }
    """
    try:
        data = execute_graphql(query)
        res = []
        for a in data.get("acoes", []):
            res.append({
                "id": a["id"],
                "descricao": a["descricao"],
                "status": a["status"],
                "impacto": a["impacto"],
                "data_criacao": a.get("dataCriacao"),
                "data_prevista_conclusao": a.get("dataPrevistaConclusao"),
                "data_conclusao": a.get("dataConclusao"),
                "comentario_fecho": a.get("comentarioFecho"),
                "sistema_id": a.get("sistemaId"),
                "responsavel_id": a.get("responsavelId")
            })
        return res
    except Exception:
        return []

def criar_acao(payload: Dict[str, Any]) -> DummyResponse:
    mutation = """
    mutation CriarAcao($descricao: String!, $impacto: String!, $sistemaId: Int!, $responsavelId: Int, $dataPrevistaConclusao: String) {
        criarAcao(descricao: $descricao, impacto: $impacto, sistemaId: $sistemaId, responsavelId: $responsavelId, dataPrevistaConclusao: $dataPrevistaConclusao) {
            id
            descricao
        }
    }
    """
    try:
        res = execute_graphql(mutation, {
            "descricao": payload.get("descricao"),
            "impacto": payload.get("impacto"),
            "sistemaId": payload.get("sistema_id"),
            "responsavelId": payload.get("responsavel_id"),
            "dataPrevistaConclusao": payload.get("data_prevista_conclusao")
        })
        return DummyResponse(201, json_data=res.get("criarAcao"))
    except Exception as e:
        return DummyResponse(400, text=str(e))

def fechar_acao(acao_id: int, data_conclusao: Optional[str] = None, comentario: Optional[str] = None) -> DummyResponse:
    mutation = """
    mutation FecharAcao($id: Int!, $dataConclusao: String, $comentario: String) {
        fecharAcao(id: $id, dataConclusao: $dataConclusao, comentario: $comentario) {
            id
            status
        }
    }
    """
    try:
        res = execute_graphql(mutation, {"id": acao_id, "dataConclusao": data_conclusao, "comentario": comentario})
        return DummyResponse(200, json_data=res.get("fecharAcao"))
    except Exception as e:
        return DummyResponse(400, text=str(e))

def editar_acao(acao_id: int, payload: Dict[str, Any]) -> DummyResponse:
    mutation = """
    mutation EditarAcao($id: Int!, $descricao: String, $impacto: String, $status: String, $dataPrevistaConclusao: String) {
        editarAcao(id: $id, descricao: $descricao, impacto: $impacto, status: $status, dataPrevistaConclusao: $dataPrevistaConclusao) {
            id
        }
    }
    """
    try:
        res = execute_graphql(mutation, {
            "id": acao_id,
            "descricao": payload.get("descricao"),
            "impacto": payload.get("impacto"),
            "status": payload.get("status"),
            "dataPrevistaConclusao": payload.get("data_prevista_conclusao")
        })
        return DummyResponse(200, json_data=res.get("editarAcao"))
    except Exception as e:
        return DummyResponse(400, text=str(e))

def criar_sistema(payload: Dict[str, Any]) -> DummyResponse:
    mutation = """
    mutation CriarSistema($nome: String!, $linhaId: Int!, $fornecedorId: Int) {
        criarSistema(nome: $nome, linhaId: $linhaId, fornecedorId: $fornecedorId) {
            id
            nome
        }
    }
    """
    try:
        res = execute_graphql(mutation, {
            "nome": payload.get("nome"),
            "linhaId": payload.get("linha_id"),
            "fornecedorId": payload.get("fornecedor_id")
        })
        return DummyResponse(201, json_data=res.get("criarSistema"))
    except Exception as e:
        return DummyResponse(400, text=str(e))

def criar_fornecedor(payload: Dict[str, Any]) -> DummyResponse:
    mutation = """
    mutation CriarFornecedor($nome: String!, $contacto: String) {
        criarFornecedor(nome: $nome, contacto: $contacto) {
            id
            nome
        }
    }
    """
    try:
        res = execute_graphql(mutation, {
            "nome": payload.get("nome"),
            "contacto": payload.get("contacto")
        })
        return DummyResponse(201, json_data=res.get("criarFornecedor"))
    except Exception as e:
        return DummyResponse(400, text=str(e))

def editar_fornecedor(fornecedor_id: int, payload: Dict[str, Any]) -> DummyResponse:
    mutation = """
    mutation EditarFornecedor($id: Int!, $nome: String!, $contacto: String) {
        editarFornecedor(id: $id, nome: $nome, contacto: $contacto) {
            id
            nome
        }
    }
    """
    try:
        res = execute_graphql(mutation, {
            "id": fornecedor_id,
            "nome": payload.get("nome"),
            "contacto": payload.get("contacto")
        })
        return DummyResponse(200, json_data=res.get("editarFornecedor"))
    except Exception as e:
        return DummyResponse(400, text=str(e))

def get_pds_geral() -> Optional[str]:
    return "💡 PDS Geral: Todos os sistemas em monitorização contínua via RabbitMQ."

def get_pds_operador(superuser_id: int) -> Optional[str]:
    return f"💡 PDS Operador #{superuser_id}: Foco em manutenções preventivas abertas."

def get_auditoria() -> List[Dict[str, Any]]:
    return []