# 🛠️ Guia de Arquitetura & Execução - Sistema de Manutenção Fabril

Este documento descreve a estrutura completa da aplicação modular desenvolvida em **Python (FastAPI + SQLModel + Streamlit)**.

---

## 1. Dependências do Projeto (`requirements.txt`)

Instale todas as dependências do backend e frontend com:

```bash
pip install -r requirements.txt
```

---

## 2. Estrutura Modular do Projeto

```text
manutencao-api/
│
├── app/                        # 🔌 API Backend (FastAPI)
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada da API REST
│   ├── database.py             # Configuração da BD SQLite (database.db)
│   ├── models.py               # Modelos de Dados (SQLModel)
│   ├── security.py             # Encriptação Bcrypt & Tokens JWT
│   ├── seed.py                 # Povoamento inicial de dados
│   ├── routers/
│   │   ├── acoes.py            # Endpoints de Ações (Criar, Editar, Fechar)
│   │   ├── auth.py             # Login, Perfil e Reset de Password
│   │   ├── superusers.py       # Listagem de Operadores/Superutilizadores
│   │   ├── estrutura.py        # Fábricas, Linhas, Sistemas e Fornecedores
│   │   ├── auditoria.py        # Histórico de Registos de Auditoria
│   │   └── pds.py              # Ponto de Situação por IA (OpenRouter)
│   └── services/
│       └── ai_service.py       # Integração com modelos LLM via OpenRouter
│
├── dashboard_ui/               # 🎨 Frontend Modular (Streamlit)
│   ├── __init__.py
│   ├── api_client.py           # Cliente HTTP centralizado com envio de JWT
│   ├── components/
│   │   └── cascade_selectors.py # Componente de seleção em cascata (Fábrica -> Linha -> Sistema)
│   └── views/
│       ├── pds_view.py          # 🤖 Ponto de Situação com IA
│       ├── registar_acao_view.py # ➕ Form de Registo de Ações
│       ├── gestao_acoes_view.py  # 🔄 Gestão, Edição e Encerramento de Ações
│       ├── analise_status_view.py# 📊 Tabela de Equipamentos e Consulta de Ações
│       ├── estrutura_view.py     # ⚙️ Adicionar Sistemas, Fornecedores e Fábricas
│       └── auditoria_view.py     # 📜 Linha do Tempo e Histórico de Logs
│
├── dashboard.py                # Ponto de entrada da UI Streamlit
├── requirements.txt
└── docs-help/                  # Documentação e Guias
    ├── endpoints-api.md        # Documentação completa de todas as rotas da API
    └── sql-help.md             # Cheat Sheet de operações SQL & SQLite
```

---

## 3. Como Executar a Aplicação

### Passo 1: Iniciar o Backend (FastAPI)
Num terminal na pasta `manutencao-api`:
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- **Documentação Swagger Interativa:** `http://localhost:8000/docs`

### Passo 2: Iniciar o Frontend Modular (Streamlit)
Noutro terminal na pasta `manutencao-api`:
```bash
streamlit run dashboard.py
```
- **Painel Interativo:** `http://localhost:8501`