from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
import app.models
from app.routers import estrutura, acoes, pds, auth, auditoria, superusers
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Tudo o que estiver ANTES do yield executa no arranque (Startup)
    create_db_and_tables()
    yield
    # Tudo o que estiver DEPOIS do yield executaria ao desligar (Shutdown - opcional)


app = FastAPI(
    title="Consola de Manutenção - API",
    version="1.0.0",
    lifespan=lifespan
)

# 🌐 Configuração de CORS (Permite chamadas do React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção podes restringir para "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#registar os routers da FastAPI
app.include_router(auth.router)
app.include_router(superusers.router)
app.include_router(estrutura.router)
app.include_router(acoes.router)
app.include_router(pds.router)
app.include_router(auditoria.router)



@app.get("/")
def health_check():
    return {"status": "ok", "mensagem": "API em Python pronta!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)