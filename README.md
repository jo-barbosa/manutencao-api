# 🛠️ Consola de Manutenção Industrial (Microserviços, RabbitMQ & GraphQL Gateway)

Sistema de gestão e acompanhamento de manutenção industrial para unidades fabris. A plataforma permite monitorizar o estado operacional de equipamentos (🟢 **OPERACIONAL**, 🟡 **DEGRADADO**, 🔴 **PARADO**), gerir intervenções técnicas e auditar alterações através de uma interface intuitiva em Streamlit organizada por fábricas.

A arquitetura do backend é baseada em **Microserviços Orientados a Eventos** com **Database-per-Service**, interligados por **RabbitMQ** (Pub/Sub), semeados por **Bootstrap Condicional Autónomo** e expostos através de um **GraphQL Gateway** unificado.

---

## 🚀 Tecnologias e Arquitetura

- **Microserviços (FastAPI + Strawberry GraphQL):** Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/), [Strawberry GraphQL](https://strawberry.rocks/) e [SQLModel](https://sqlmodel.tiangolo.com/).
- **Broker de Mensagens (Event-Driven):** [RabbitMQ](https://www.rabbitmq.com/) (`pika` / `aio-pika`) com arquitetura Pub/Sub baseada em tópicos (`acao.criada`, `acao.atualizada`, `acao.fechada`).
- **Bootstrap de Dados Autónomo:** Cada microserviço verifica e popula automaticamente a sua própria base de dados no arranque apenas se esta se encontrar vazia (`bootstrap.py`).
- **GraphQL Gateway:** Ponto único de entrada (`:8000/graphql`) que agrega e roteia as consultas e mutações federadas com verificação por expressões regulares e *word boundaries* (`\b`).
- **Frontend (Streamlit):** Interface modular em [Streamlit](https://streamlit.io/) com cliente GraphQL unificado ([dashboard_ui/api_client.py](file:///home/barjor/PycharmProjects/manutencao-api/dashboard_ui/api_client.py)), contendo um painel em tempo real dividido em **3 colunas de fábricas** com cartões e semáforos unificados.
- **Bases de Dados (Database-per-Service):** Persistência autónoma para cada domínio (`auth.db`, `estrutura.db`, `manutencao.db`), prevenindo acoplamento.
- **Configuração & Orquestração:** Centralização via `.env` / `.env.example`, Docker, Docker Compose, `start.sh` e `Makefile`.

---

## 📂 Arquitetura da Estrutura de Pastas

```text
manutencao-api/
│
├── services/                      # 🧱 Microserviços Autónomos (Bounded Contexts)
│   ├── auth_service/              # 🔐 Autenticação, Utilizadores & Tokens JWT
│   │   ├── main.py                # Ponto de entrada FastAPI (:8001)
│   │   ├── bootstrap.py           # Bootstrap de utilizadores iniciais
│   │   ├── models.py              # Modelo de Superuser
│   │   ├── database.py            # Base de dados isolada (auth.db)
│   │   ├── schema.py              # Esquema Strawberry GraphQL (login, me, superusers)
│   │   └── security.py            # Hashing PBKDF2/Bcrypt e tokens JWT
│   │
│   ├── estrutura_service/         # 🏭 Fábricas, Linhas, Sistemas & Fornecedores
│   │   ├── main.py                # Ponto de entrada FastAPI (:8002)
│   │   ├── bootstrap.py           # Bootstrap da estrutura fabril inicial
│   │   ├── models.py              # Modelos da estrutura fabril
│   │   ├── database.py            # Base de dados isolada (estrutura.db)
│   │   ├── schema.py              # Esquema Strawberry GraphQL
│   │   └── event_consumer.py      # 🐰 Consumidor RabbitMQ (atualiza estado do sistema)
│   │
│   └── manutencao_service/        # 🛠️ Ações de Manutenção & Intervenções
│       ├── main.py                # Ponto de entrada FastAPI (:8003)
│       ├── bootstrap.py           # Bootstrap de ações de manutenção iniciais
│       ├── models.py              # Modelo de Ação de Manutenção
│       ├── database.py            # Base de dados isolada (manutencao.db)
│       ├── schema.py              # Esquema Strawberry GraphQL
│       └── event_publisher.py     # 📤 Publicador RabbitMQ (eventos de ações)
│
├── gateway/                       # 🌐 GraphQL Gateway (Porta :8000/graphql)
│   └── main.py                    # Roteamento e agregação inteligente de requisições GraphQL
│
├── dashboard_ui/                  # 🎨 Package Frontend Modular em Streamlit
│   ├── api_client.py              # Cliente GraphQL de comunicação com o Gateway
│   ├── layout.py                  # Cabeçalho e estrutura visual comum
│   ├── components/                # Componentes reutilizáveis (ex.: seleção em cascata)
│   └── views/                     # Visões (Análise, Estrutura, Gestão, Auditoria)
├── dashboard.py                   # Ponto de entrada da aplicação Streamlit (:8501)
│
├── docs-help/                     # 📚 Guias e Documentação Auxiliar
│   ├── docker-deployment.md       # Guia de implantação offline (docker save / docker load)
│   ├── endpoints-api.md           # Referência de esquemas GraphQL
│   └── sql-help.md                # Referência de BD e consultas
├── CONTEXT.md                     # Linguagem Ubíqua & Bounded Contexts
│
├── .env                           # Variáveis de ambiente locais
├── .env.example                   # Template de variáveis de ambiente
├── docker-compose.yml             # Orquestração (RabbitMQ + 3 Microserviços + Gateway + Dashboard)
├── Dockerfile                     # Containerização genérica dos microserviços Python
├── start.sh                       # Script bash de arranque automático
├── Makefile                       # Atalhos de terminal (make start, make stop, make logs)
└── requirements.txt               # Dependências do projeto
```

---

## 📐 Princípios de Arquitetura (DDD & Clean Architecture)

1. **Separação por Bounded Contexts (`services/`):** Cada microserviço reside no seu próprio diretório com modelos de dados, base de dados, esquemas GraphQL e lógica de negócio 100% isolados.
2. **Desacoplamento por Eventos (RabbitMQ):** O `manutencao_service` apenas publica eventos (`acao.criada`, `acao.atualizada`, `acao.fechada`). O `estrutura_service` consome as mensagens em background através do `event_consumer.py`, mantendo a consistência eventual sem acoplamento entre bases de dados.
3. **Ponto Único de Comunicação (`gateway/`):** O frontend comunica exclusivamente com o GraphQL Gateway (`/graphql`), abstraindo a topologia interna.
4. **Isolamento de Persistência (*Database-per-Service*):** Garante que nenhum microserviço lê ou escreve diretamente na base de dados de outro microserviço.

---

## ⚡ Como Executar o Projeto no Terminal

### Método 1: Via Script de Arranque (Recomendado)

Na raiz do projeto, execute o script `./start.sh`:

```bash
./start.sh
```

### Método 2: Via Docker Compose / Makefile

```bash
docker compose up -d
# ou
make start
```

Para verificar logs ou parar os serviços:
```bash
make logs   # Visualizar logs em tempo real
make stop   # Parar todos os containers
```

---

## 🌐 Endpoints e Portas do Sistema

| Serviço | URL / Endpoint | Descrição |
| :--- | :--- | :--- |
| 📊 **Dashboard Frontend** | `http://localhost:8501` | Interface de utilizador Streamlit |
| 🌐 **GraphQL Gateway** | `http://localhost:8000/graphql` | Endpoint unificado de GraphQL |
| 🐰 **RabbitMQ Management** | `http://localhost:15672` | Painel de gestão RabbitMQ (user: `guest` / pass: `guest`) |
| 🔐 **Auth-Service** | `http://localhost:8001/graphql` | Microserviço de Autenticação |
| 🏭 **Estrutura-Service** | `http://localhost:8002/graphql` | Microserviço de Estrutura Fabril |
| 🛠️ **Manutenção-Service** | `http://localhost:8003/graphql` | Microserviço de Ações de Manutenção |
