# 🛠️ Consola de Manutenção Industrial (Python API & Streamlit Dashboard)

Sistema de gestão e acompanhamento de manutenção industrial para unidades fabris. A aplicação permite monitorizar o estado operacional de equipamentos (🟢 **OPERACIONAL**, 🟡 **DEGRADADO**, 🔴 **PARADO**), gerir intervenções técnicas, auditar alterações e gerar Pontos de Situação (PDS) inteligentes com integração de IA.

---

## 🚀 Tecnologias Utilizadas

- **Backend (API REST):** Python 3.12, [FastAPI](https://fastapi.tiangolo.com/), [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic), Uvicorn.
- **Frontend (Interface de Utilizador):** [Streamlit](https://streamlit.io/) (Navegação Dinâmica Multipágina).
- **Segurança & Autenticação:** HTTP Bearer JWT (`python-jose`), Encriptação de passwords (`bcrypt`).
- **Bases de Dados Suportadas:**
  - 🛠️ **SQLite** (Desenvolvimento Local Padrão)
  - 🐘 **PostgreSQL 16** (Produção Docker / Windows Server)
- **Containerização:** Docker & Docker Compose.

---

## 📂 Arquitetura do Projeto

```text
manutencao-api/
│
├── app/                        # 🔌 Backend FastAPI
│   ├── main.py                 # Ponto de entrada e configuração dos routers REST
│   ├── database.py             # Suporte híbrido a PostgreSQL e SQLite via DATABASE_URL
│   ├── models.py               # Modelos de dados e enums (SQLModel)
│   ├── security.py             # Encriptação Bcrypt e emissão/validação de JWT
│   ├── seed.py                 # Script de povoamento inicial de dados
│   ├── routers/                # Endpoints (ações, auth, superusers, estrutura, auditoria, pds)
│   └── services/               # Serviço de IA via OpenRouter com fallback automático
│
├── dashboard_ui/               # 📦 Package Frontend Modular em Streamlit
├── dashboard.py                # Ponto de entrada da aplicação Streamlit (Multipágina)
├── Dockerfile                  # Containerização de Produção
├── docker-compose.yml          # Orquestração Produção (PostgreSQL + API + Dashboard)
├── docker-compose.sqlite.yml   # Orquestração Local com SQLite
├── requirements.txt            # Dependências Python (incluindo psycopg2-binary)
└── docs-help/                  # Documentação Técnica e Endpoints
```

---

## 🐘 Suporte Híbrido a Bases de Dados (SQLite vs PostgreSQL)

O ficheiro `app/database.py` deteta automaticamente o tipo de BD através da variável de ambiente `DATABASE_URL`:

- **Desenvolvimento (SQLite por defeito):**
  ```env
  DATABASE_URL=sqlite:///database.db
  ```
- **Produção (PostgreSQL em Docker/Windows Server):**
  ```env
  DATABASE_URL=postgresql://postgres:fabrica_password_2026@postgres-db:5432/maintenancedb
  ```

---

## 🐳 Implantação em Produção com Docker (Windows Server)

### Requisitos no Windows Server:
1. Instalar o **Docker Desktop para Windows** (ou Docker Engine no WSL2/Hyper-V).
2. Ativar o suporte a **Linux Containers**.

### 1. Iniciar toda a Infraestrutura (PostgreSQL + API + Dashboard)
Na pasta do projeto, execute no PowerShell ou CMD:

```powershell
docker compose up -d --build
```

Este comando vai iniciar 3 contentores em segundo plano:
- 🐘 `manutencao-postgres` (PostgreSQL 16 na porta `5432` com volume persistente `pgdata_manutencao`)
- 🔌 `manutencao-api-backend` (API FastAPI na porta `8000`)
- 🎨 `manutencao-streamlit-dashboard` (Dashboard Streamlit na porta `8501`)

### 2. Povoar Dados Iniciais no PostgreSQL (Seed)
Após subir os contentores, execute o script de seed dentro do contentor da API:

```powershell
docker exec -it manutencao-api-backend python -m app.seed
```

### 3. Testes Rápidos em Docker com SQLite (Sem Postgres)
Se quiser testar a aplicação em Docker usando SQLite:

```powershell
docker compose -f docker-compose.sqlite.yml up -d --build
```

---

## 💻 Execução Local sem Docker

### 1. Instalar Dependências
```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
```

### 2. Iniciar Serviços
- **Backend FastAPI:**
  ```bash
  python -m uvicorn app.main:app --reload --port 8000
  ```
- **Frontend Streamlit:**
  ```bash
  python -m streamlit run dashboard.py
  ```

---

## 🔑 Credenciais de Acesso (Dados de Teste)

| Função | Email | Password |
| :--- | :--- | :--- |
| **Operador Principal** | `jorge.barbosa@inter.ikea.com` | `dummy` |
| **Técnico de Manutenção** | `helder.vieira@inter.ikea.com` | `dummy` |
| **Técnico de Manutenção** | `helio.machado1@inter.ikea.com` | `dummy` |
