# 🛠️ Consola de Manutenção Industrial (Python API & Streamlit Dashboard)

Sistema de gestão e acompanhamento de manutenção industrial para unidades fabris. A aplicação permite monitorizar o estado operacional de equipamentos (🟢 **OPERACIONAL**, 🟡 **DEGRADADO**, 🔴 **PARADO**), gerir intervenções técnicas, auditar alterações e gerar Pontos de Situação (PDS) inteligentes com integração de IA.

---

## 🚀 Tecnologias Utilizadas

- **Backend (API REST):** Python 3.12, [FastAPI](https://fastapi.tiangolo.com/), [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic), Uvicorn.
- **Frontend (Interface de Utilizador):** [Streamlit](https://streamlit.io/) (Navegação Dinâmica Multipágina com `st.navigation`).
- **Segurança & Autenticação:** HTTP Bearer JWT (`python-jose`), Encriptação de passwords (`bcrypt`).
- **Inteligência Artificial (PDS):** Integração via OpenRouter API (Llama 3.3, Gemini 2.5, DeepSeek) com fallback automático.
- **Base de Dados:** SQLite local (`database.db`).

---

## 📂 Arquitetura do Projeto

```text
manutencao-api/
│
├── app/                        # 🔌 Backend FastAPI
│   ├── main.py                 # Ponto de entrada e configuração dos routers REST
│   ├── database.py             # Ligação e motor da base de dados SQLite
│   ├── models.py               # Modelos de dados e enums (SQLModel)
│   ├── security.py             # Encriptação Bcrypt e emissão/validação de JWT
│   ├── seed.py                 # Script de povoamento inicial de dados de teste
│   ├── routers/
│   │   ├── acoes.py            # Criar, editar, listar e fechar ações (recálculo de estado)
│   │   ├── auth.py             # Login, perfil, registo e alteração de password
│   │   ├── superusers.py       # Listagem de operadores/técnicos
│   │   ├── estrutura.py        # Gestão de Fábricas, Linhas, Sistemas e Fornecedores
│   │   ├── auditoria.py        # Histórico cronológico de operações
│   │   └── pds.py              # Ponto de Situação inteligente (IA)
│   └── services/
│       └── ai_service.py       # Serviço de IA via OpenRouter com fallback automático
│
├── dashboard_ui/               # 📦 Package Frontend Modular em Streamlit
│   ├── home.py                 # Vista principal do Dashboard (Métricas, PDS e Tabela)
│   ├── api_client.py           # Cliente HTTP centralizado para comunicação com a API
│   ├── auth_guard.py           # Guarda de segurança para páginas restritas
│   ├── components/
│   │   └── cascade_selectors.py # Dropdowns encadeados (Fábrica -> Linha -> Sistema)
│   └── views/
│       ├── pds_view.py          # Relatórios executivos e briefing de operador
│       ├── registar_acao_view.py # Form de registo de nova ação de manutenção
│       ├── gestao_acoes_view.py  # Edição e encerramento de avarias
│       ├── analise_status_view.py# Consulta avançada e cartões de intervenções
│       ├── estrutura_view.py     # Criação de equipamentos, linhas e fornecedores
│       └── auditoria_view.py     # Feed cronológico de auditoria
│
├── dashboard.py                # Ponto de entrada da aplicação Streamlit (Multipágina)
├── requirements.txt            # Ficheiro de dependências Python
└── docs-help/                  # Documentação Técnica
    ├── endpoints-api.md        # Documentação completa de todos os endpoints REST
    └── sql-help.md             # Guia de comandos SQL e SQLite
```

---

## ⚡ Instalação e Execução

### 1. Criar e Ativar Ambiente Virtual

```bash
# Na raiz da pasta manutencao-api
python3 -m venv .venv

# Ativar no Linux/macOS:
source .venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Povoar a Base de Dados (Opcional)

Para carregar dados de exemplo (Fábricas, Linhas, Sistemas, Fornecedores e Utilizadores):

```bash
python -m app.seed
```

---

## ⚙️ Como Iniciar as Aplicações

### 1. Iniciar o Backend (API FastAPI)
Abra um terminal e execute:

```bash
./.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```
- **API REST Base:** `http://localhost:8000/api`
- **Documentação Swagger Interativa:** `http://localhost:8000/docs`

### 2. Iniciar o Frontend (Dashboard Streamlit)
Noutro terminal, execute:

```bash
./.venv/bin/streamlit run dashboard.py
```
- **Painel Web:** `http://localhost:8501`

---

## 🔑 Credenciais de Acesso (Dados de Teste)

| Função | Email | Password |
| :--- | :--- | :--- |
| **Operador Principal** | `jorge.barbosa@inter.ikea.com` | `dummy` |
| **Técnico de Manutenção** | `helder.vieira@inter.ikea.com` | `dummy` |
| **Técnico de Manutenção** | `helio.machado1@inter.ikea.com` | `dummy` |

---

## 📋 Resumo dos Endpoints da API

| Método | Endpoint | Descrição |
| :---: | :--- | :--- |
| `POST` | `/api/auth/login` | Autenticação e emissão de Token JWT |
| `GET` | `/api/superusers` | Lista todos os operadores registados |
| `GET` | `/api/sistemas/status` | Tabela achatada do estado dos equipamentos |
| `POST` | `/api/acoes` | Regista nova ação e recalcula estado do equipamento |
| `PUT` | `/api/acoes/{id}/fechar` | Encerra ação e repõe estado a **OPERACIONAL** |
| `PUT` | `/api/acoes/{id}` | Edita dados de uma ação existente |
| `GET` | `/api/pds/geral` | Resumo executivo da fábrica via IA |
| `GET` | `/api/pds/operador/{id}` | Briefing personalizado do turno do operador via IA |
| `GET` | `/api/auditoria` | Histórico cronológico de operações efetuadas |

*(Consulte a documentação completa em [`docs-help/endpoints-api.md`](docs-help/endpoints-api.md))*

---

## 💡 Principais Funcionalidades da Interface

1. **Dashboard Inicial (Público/Autenticado):**
   - **PDS Inteligente (1.º lugar):** PDS Geral da fábrica sem login; PDS do Operador após login.
   - **Semáforos de Estado (2.º lugar):** Contagem de equipamentos Operacionais, Degradados, Parados e Ações Abertas.
   - **Lista de Equipamentos (3.º lugar):** Tabela em tempo real de todos os sistemas fabris.
2. **Navegação Dinâmica (Sidebar):**
   - Antes do login, a barra lateral exibe apenas a opção `Dashboard` e o formulário de login.
   - Após o login, são desbloqueadas as secções de **Operação Fabril** e **Gestão & Consulta**.
3. **Gestão de Ações:**
   - Encerramento de avarias com registo de data e comentário, recalculando automaticamente se a máquina regressa a `OPERACIONAL`.
