# Contexto do Domínio - Sistema de Manutenção Fabril

## Bounded Contexts

### 1. Contexto de Autenticação (`Auth-Service`)
* **Superuser**: Utilizador com permissões administrativas e de intervenção técnica na plataforma.
* **Token JWT**: Mecanismo de autenticação e identificação de identidade utilizado nas operações.

### 2. Contexto de Estrutura Fabril (`Estrutura-Service`)
* **Fábrica**: Unidade fabril onde ocorrem as operações industriais (ex: PIGMENT, PFF, BOF).
* **Linha**: Linha de produção pertencente a uma Fábrica.
* **Sistema / Equipamento**: Máquina ou conjunto de equipamentos instalados numa Linha de produção.
* **Fornecedor**: Entidade externa responsável por fornecer ou dar assistência técnica a um Sistema.
* **Estado do Sistema**: Classificação operacional do equipamento (`OPERACIONAL`, `DEGRADADO`, `PARADO`), calculado assincronamente via eventos.

### 3. Contexto de Ações de Manutenção (`Manutencao-Service`)
* **Ação de Manutenção**: Intervenção técnica ou registo de avaria num Sistema. Possui estado (`ABERTA`, `FECHADA`) e um nível de impacto (`TOTAL`, `PARCIAL`, `NENHUM`).
* **Evento de Manutenção**: Notificação assíncrona publicada no broker de mensagens sempre que uma Ação é criada, editada ou encerrada.

---

## Eventos do Domínio (RabbitMQ)

* `acao.criada`: Disparado quando uma nova ação de manutenção é registada.
* `acao.atualizada`: Disparado quando os dados ou impacto de uma ação são alterados.
* `acao.fechada`: Disparado quando uma ação é dada como concluída pelo técnico.
