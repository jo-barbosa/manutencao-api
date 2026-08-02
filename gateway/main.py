import os
from typing import Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001/graphql")
ESTRUTURA_SERVICE_URL = os.getenv("ESTRUTURA_SERVICE_URL", "http://localhost:8002/graphql")
MANUTENCAO_SERVICE_URL = os.getenv("MANUTENCAO_SERVICE_URL", "http://localhost:8003/graphql")

app = FastAPI(title="GraphQL Gateway (Federated Microservices)", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def forward_graphql(target_url: str, request: Request) -> Response:
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(target_url, content=body, headers=headers)
        return Response(content=res.content, status_code=res.status_code, media_type=res.headers.get("content-type"))

@app.post("/graphql")
async def graphql_gateway(request: Request):
    try:
        body_json = await request.json()
        query = body_json.get("query", "")

        # Encaminhamento inteligente com base na query/mutação enviada
        if any(keyword in query for keyword in ["login", "criarSuperuser", "superusers", "me"]):
            target = AUTH_SERVICE_URL
        elif any(keyword in query for keyword in ["fabricas", "linhas", "sistemas", "fornecedores", "criarFabrica", "criarLinha", "criarSistema", "criarFornecedor", "editarFornecedor"]):
            target = ESTRUTURA_SERVICE_URL
        else:
            target = MANUTENCAO_SERVICE_URL

        return await forward_graphql(target, request)
    except Exception as e:
        err_msg = str(e).replace('"', '\\"')
        return Response(content=f'{{"errors": [{{"message": "{err_msg}"}}]}}', status_code=500, media_type="application/json")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "graphql-gateway",
        "services": {
            "auth": AUTH_SERVICE_URL,
            "estrutura": ESTRUTURA_SERVICE_URL,
            "manutencao": MANUTENCAO_SERVICE_URL
        }
    }
