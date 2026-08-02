# 🛠️ Consola de Manutenção Industrial (Microserviços, RabbitMQ & GraphQL Gateway)

Sistema de gestão e acompanhamento de manutenção industrial para unidades fabris. A plataforma permite monitorizar o estado operacional de equipamentos (🟢 **OPERACIONAL**, 🟡 **DEGRADADO**, 🔴 **PARADO**), gerir intervenções técnicas e auditar alterações.

A arquitetura do backend é baseada em **Microserviços Orientados a Eventos** com **Database-per-Service**, interligados por **RabbitMQ** e expostos através de um **GraphQL Gateway** unificado.

---

## 🚀 Tecnologias e Arquitetura

- **Microserviços (FastAPI + Strawberry GraphQL):** Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/), [Strawberry GraphQL](https://strawberry.rocks/) e [SQLModel](https://sqlmodel.tiangolo.com/).
- **Broker de Mensagens (Event-Driven):** [RabbitMQ](https://www.rabbitmq.com/) (`pika` / `aio-pika`) com arquitetura Pub/Sub baseada em tópicos (`acao.criada`, `acao.atualizada`, `acao.fechada`).
- **GraphQL Gateway:** Ponto único de entrada (`/graphql`) que agrega e roteia as consultas e mutações federadas para os respetivos microserviços.
- **Frontend:** [Streamlit](https://streamlit.io/) com cliente GraphQL unificado ([dashboard_ui/api_client.py](file:///home/barjor/PycharmProjects/manutencao-api/dashboard_ui/api_client.py)).
- **Bases de Dados (Database-per-Service):** Bases de dados autónomas para cada domínio (`auth.db`, `estrutura.db`, `manutencao.db`), prevenindo o acoplamento de dados.
- **Orquestração & DX:** Docker, Docker Compose, `start.sh` e `Makefile`.

---

## 📂 Arquitetura da Estrutura de Pastas

```text
manutencao-api/
│
├── services/                      # 🧱 Microserviços Autónomos (Bounded Contexts)
│   ├── auth_service/              # 🔐 Autenticação, Utilizadores & Tokens JWT
│   │   ├── main.py                # Ponto de entrada FastAPI (:8001)
│   │   ├── models.py              # Modelo de Superuser
│   │   ├── database.py            # Base de dados isolada (auth.db)
│   │   ├── schema.py              # Esquema Strawberry GraphQL (login, me, superusers)
│   │   └── security.py            # Hashing Bcrypt e JWT
│   │
│   ├── estrutura_service/         # 🏭 Fábricas, Linhas, Sistemas & Fornecedores
│   │   ├── main.py                # Ponto de entrada FastAPI (:8002)
│   │   ├── models.py              # Modelos da estrutura fabril
│   │   ├── database.py            # Base de dados isolada (estrutura.db)
│   │   ├── schema.py              # Esquema Strawberry GraphQL
│   │   └── event_consumer.py      # 🐰 Consumidor RabbitMQ (atualiza estado do sistema)
│   │
│   └── manutencao_service/        # 🛠️ Ações de Manutenção & Intervenções
│       ├── main.py                # Ponto de entrada FastAPI (:8003)
│       ├── models.py              # Modelo de Ação de Manutenção
│       ├── database.py            # Base de dados isolada (manutencao.db)
│       ├── schema.py              # Esquema Strawberry GraphQL
│       └── event_publisher.py     # 📤 Publicador RabbitMQ (eventos de ações)
│
├── gateway/                       # 🌐 GraphQL Gateway (Porta :8000/graphql)
│   └── main.py                    # Roteamento e agregação das requisições GraphQL
│
├── dashboard_ui/                  # 🎨 Package Frontend Modular em Streamlit
│   ├── api_client.py              # Cliente GraphQL de comunicação com o Gateway
│   └── views/                     # Visões e componentes da interface
├── dashboard.py                   # Ponto de entrada da aplicação Streamlit (:8501)
│
├── docs/                          # 📚 Documentação Técnica & Arquitetura
│   └── adr/                       # Registos de Decisões de Arquitetura (ADR 0001)
├── CONTEXT.md                     # Linguagem Ubíqua & Bounded Contexts
│
├── docker-compose.yml             # Orquestração (RabbitMQ + 3 Microserviços + Gateway + Dashboard)
├── Dockerfile                     # Containerização genérica dos microserviços Python
├── start.sh                       # Script bash para arranque rápido no terminal
├── Makefile                       # Atalhos de terminal (make start, make stop, make logs)
└── requirements.txt               # Dependências do projeto (incluindo Strawberry GraphQL & pika)
```

---

## 📐 Avaliação da Organização da Arquitetura

A estrutura de pastas encontra-se organizada de acordo com os princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**:

1. **Separação por Bounded Contexts (`services/`):** Cada microserviço reside no seu próprio diretório com modelos de dados, base de dados, esquemas GraphQL e lógica de negócio 100% isolados.
2. **Desacoplamento por Eventos (RabbitMQ):** O `manutencao_service` apenas envia mensagens sobre ações de manutenção. O `estrutura_service` consome as mensagens em background através do `event_consumer.py`, mantendo a consistência eventual sem chamadas síncronas entre bases de dados.
3. **Ponto Único de Comunicação (`gateway/`):** O frontend comunica exclusivamente com o GraphQL Gateway (`/graphql`), abstraindo a topologia de portas dos microserviços.
4. **Isolamento de Persistência (*Database-per-Service*):** Garante que nenhum microserviço lê ou escreve diretamente na base de dados de outro microserviço.

---

## ⚡ Como Executar o Projeto no Terminal

### Método 1: Via Script de Arranque (Recomendado)

Na raiz do projeto, execute o script `./start.sh`:

```bash
./start.sh
```

### Método 2: Via Makefile

```bash
make start
```

Para verificar logs ou parar os serviços:
```bash
make logs   # Visualizar logs em tempo real
make stop   # Parar todos os containers
```

---

## 🌐 Endpoints e Portas do Sistema

Após o arranque, os seguintes serviços estarão disponíveis:

| Serviço | URL / Endpoint | Descrição |
| :--- | :--- | :--- |
| 📊 **Dashboard Frontend** | `http://localhost:8501` | Interface de utilizador Streamlit |
| 🌐 **GraphQL Gateway** | `http://localhost:8000/graphql` | Endpoint unificado de GraphQL |
| 🐰 **RabbitMQ Management** | `http://localhost:15672` | Painel de gestão RabbitMQ (user: `guest` / pass: `guest`) |
| 🔐 **Auth-Service** | `http://localhost:8001/graphql` | Microserviço de Autenticação |
| 🏭 **Estrutura-Service** | `http://localhost:8002/graphql` | Microserviço de Estrutura Fabril |
| 🛠️ **Manutenção-Service** | `http://localhost:8003/graphql` | Microserviço de Ações de Manutenção |

