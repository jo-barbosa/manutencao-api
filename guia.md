# 🛠️ Guia de Arquitetura & Execução - Sistema de Manutenção Fabril

Este documento descreve a estrutura completa, componentes e procedimentos de execução da aplicação de manutenção fabril desenvolvida em **Python (FastAPI + Strawberry GraphQL + RabbitMQ + Streamlit)**.

---

## 1. Instalação e Dependências (`requirements.txt`)

Instale todas as dependências da aplicação com:

```bash
pip install -r requirements.txt
```

---

## 2. Estrutura Modular do Projeto (Microserviços & Event-Driven)

```text
manutencao-api/
│
├── services/                      # 🧱 Microserviços Autónomos (Bounded Contexts)
│   ├── auth_service/              # 🔐 Autenticação & Gestão de Tokens JWT (:8001)
│   │   ├── main.py                # Ponto de entrada FastAPI & lifecycle hooks
│   │   ├── bootstrap.py           # População inicial condicional (auth.db)
│   │   ├── models.py              # Modelo de dados Superuser
│   │   ├── database.py            # Configuração e engine da BD
│   │   ├── schema.py              # Esquema Strawberry GraphQL
│   │   └── security.py            # Hashing PBKDF2/Bcrypt & Tokens JWT
│   │
│   ├── estrutura_service/         # 🏭 Fábricas, Linhas, Sistemas & Fornecedores (:8002)
│   │   ├── main.py                # Ponto de entrada FastAPI
│   │   ├── bootstrap.py           # População inicial da estrutura fabril (estrutura.db)
│   │   ├── models.py              # Modelos Fabrica, Linha, Sistema, Fornecedor
│   │   ├── database.py            # Configuração e engine da BD
│   │   ├── schema.py              # Esquema Strawberry GraphQL
│   │   └── event_consumer.py      # Consumidor RabbitMQ (recálculo de estado do sistema)
│   │
│   └── manutencao_service/        # 🛠️ Gestão de Intervenções e Ações de Manutenção (:8003)
│       ├── main.py                # Ponto de entrada FastAPI
│       ├── bootstrap.py           # População inicial de ações de teste (manutencao.db)
│       ├── models.py              # Modelo de dados Acao
│       ├── database.py            # Configuração e engine da BD
│       ├── schema.py              # Esquema Strawberry GraphQL
│       └── event_publisher.py     # Publicador de eventos RabbitMQ (Pub/Sub)
│
├── gateway/                       # 🌐 Federated GraphQL Gateway (:8000/graphql)
│   └── main.py                    # Roteamento inteligente de consultas e mutações
│
├── dashboard_ui/                  # 🎨 Frontend Modular (Streamlit)
│   ├── api_client.py              # Cliente GraphQL unificado
│   ├── layout.py                  # Componente de cabeçalho comum
│   ├── components/
│   │   └── cascade_selectors.py   # Seletor em cascata (Fábrica -> Linha -> Sistema)
│   └── views/
│       ├── registar_page.py       # ➕ Registo de Ações de Manutenção
│       ├── gestao_page.py         # 🔄 Edição e Encerramento de Ações
│       ├── analise_page.py        # 📊 Análise e Consulta de Equipamentos
│       ├── estrutura_page.py      # ⚙️ Gestão de Sistemas e Fornecedores
│       └── auditoria_page.py      # 📜 Linha do Tempo e Histórico de Logs
│
├── dashboard.py                   # Ponto de entrada da UI Streamlit (:8501)
├── .env                           # Variáveis de ambiente locais
├── .env.example                   # Template de variáveis de ambiente
├── docker-compose.yml             # Orquestração (RabbitMQ + Microserviços + Gateway + UI)
├── Dockerfile                     # Imagem Docker multi-stage dos serviços Python
├── start.sh                       # Script de execução rápida
├── Makefile                       # Atalhos de comandos
└── docs-help/                     # Documentação Auxiliar
    ├── docker-deployment.md       # Guia de implantação offline (docker save / docker load)
    ├── endpoints-api.md           # Referência de esquemas GraphQL
    └── sql-help.md                # Cheat Sheet de operações SQL & SQLite
```

---

## 3. Como Executar a Aplicação

### Opção 1: Via Script Automático (Recomendado)
Num terminal na pasta `manutencao-api`:
```bash
./start.sh
```

### Opção 2: Via Docker Compose
```bash
docker compose up -d
```

### Opção 3: Via Makefile
```bash
make start      # Iniciar todos os containers
make logs       # Acompanhar logs em tempo real
make stop       # Parar todos os containers
```

---

## 4. Bootstrap Condicional de Dados
Cada microserviço executa autonomamente o seu script `bootstrap.py` durante o arranque (`startup`). Caso a respetiva base de dados esteja vazia, os registos iniciais são inseridos automaticamente:

- **Auth-Service (`auth.db`):** Cria os utilizadores iniciais (`admin@empresa.com` / `admin123`, `joao.silva@empresa.com` / `senha123`, etc.).
- **Estrutura-Service (`estrutura.db`):** Cria as fábricas (*PIGMENT*, *NORDIC*, *PACOS_1*), linhas de produção, fornecedores e equipamentos.
- **Manutenção-Service (`manutencao.db`):** Cria o histórico inicial de ações de manutenção.

---

## 5. Guias Complementares de Implantação
Para instruções detalhadas de exportação e implantação offline em servidores de produção sem acesso direto a registos públicos, consulte o guia em **[docs-help/docker-deployment.md](file:///home/barjor/PycharmProjects/manutencao-api/docs-help/docker-deployment.md)**.