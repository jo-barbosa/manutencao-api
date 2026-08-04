from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from services.auditoria_service.database import init_db
from services.auditoria_service.bootstrap import bootstrap_auditoria_data
from services.auditoria_service.schema import schema
from services.auditoria_service.event_consumer import start_auditoria_consumer_thread

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    bootstrap_auditoria_data()
    start_auditoria_consumer_thread()
    yield

app = FastAPI(title="Auditoria-Service (Microservice)", version="2.0.0", lifespan=lifespan)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
def health():
    return {"status": "ok", "service": "auditoria-service"}
