# ADR 0001: Decomposição em Microserviços, GraphQL Federation e Event-Driven com RabbitMQ

* **Status:** Aceite
* **Data:** 2026-07-31

## Contexto

A aplicação de gestão de manutenção encontrava-se estruturada como um monólito FastAPI com uma base de dados SQLite única. Para melhorar o isolamento de domínios, permitir escalabilidade independente e suportar atualização assíncrona do estado dos equipamentos, foi decidido refatorar o backend.

## Decisões

1. **Decomposição em 3 Microserviços:**
   - `auth_service`: Autenticação e gestão de utilizadores.
   - `estrutura_service`: Gestão de fábricas, linhas, sistemas e fornecedores.
   - `manutencao_service`: Registo e acompanhamento das ações de manutenção.

2. **Isolamento de Persistência (Database-per-Service):**
   - Cada microserviço possui e gere a sua própria base de dados SQLite/PostgreSQL independente (`auth.db`, `estrutura.db`, `manutencao.db`).

3. **Comunicação por Eventos via RabbitMQ:**
   - O `manutencao_service` publica eventos de ciclo de vida de ações (`acao.criada`, `acao.atualizada`, `acao.fechada`).
   - O `estrutura_service` subscreve a estes eventos para atualizar assincronamente o `estado_atual` dos sistemas.

4. **GraphQL Schema Federation / Gateway:**
   - Cada microserviço expõe a sua API através de **Strawberry GraphQL**.
   - Um **GraphQL Gateway** unifica os 3 esquemas num único endpoint federado (`/graphql`).

5. **Orquestração e Execução no Terminal:**
   - Configuração de um `docker-compose.yml` unificado e um script `./start.sh` para arranque imediato via terminal.

## Consequências

- **Positivas:** Desacoplamento total dos domínios, tolerância a falhas na atualização de estados, API unificada para clientes via GraphQL.
- **Custos:** Maior complexidade na gestão de infraestrutura (broker RabbitMQ + Gateway).
