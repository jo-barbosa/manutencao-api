from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from services.auth_service.database import init_db
from services.auth_service.bootstrap import bootstrap_auth_data
from services.auth_service.schema import schema

app = FastAPI(title="Auth-Service (Microservice)", version="2.0.0")

@app.on_event("startup")
def startup():
    init_db()
    bootstrap_auth_data()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}
