from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from services.manutencao_service.database import init_db
from services.manutencao_service.bootstrap import bootstrap_manutencao_data
from services.manutencao_service.schema import schema

app = FastAPI(title="Manutencao-Service (Microservice)", version="2.0.0")

@app.on_event("startup")
def startup():
    init_db()
    bootstrap_manutencao_data()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
def health():
    return {"status": "ok", "service": "manutencao-service"}
