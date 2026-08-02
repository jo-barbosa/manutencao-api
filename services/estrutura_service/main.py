from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from services.estrutura_service.database import init_db
from services.estrutura_service.bootstrap import bootstrap_estrutura_data
from services.estrutura_service.schema import schema
from services.estrutura_service.event_consumer import run_consumer_in_background

app = FastAPI(title="Estrutura-Service (Microservice)", version="2.0.0")

@app.on_event("startup")
def startup():
    init_db()
    bootstrap_estrutura_data()
    run_consumer_in_background()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
def health():
    return {"status": "ok", "service": "estrutura-service"}
