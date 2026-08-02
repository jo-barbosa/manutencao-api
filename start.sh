#!/usr/bin/env bash
set -e

echo "🚀 A iniciar o ambiente de Microserviços + RabbitMQ + GraphQL Gateway..."

if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

echo "📦 A construir e iniciar os containers em segundo plano..."
$DOCKER_COMPOSE_CMD up --build -d

echo ""
echo "✅ Todos os serviços estão ativos!"
echo "--------------------------------------------------------"
echo "🌐 GraphQL Gateway:        http://localhost:8000/graphql"
echo "📊 Dashboard (Streamlit):  http://localhost:8501"
echo "🐰 RabbitMQ Console:       http://localhost:15672 (guest / guest)"
echo "🔑 Auth-Service:           http://localhost:8001/graphql"
echo "🏭 Estrutura-Service:      http://localhost:8002/graphql"
echo "🛠️  Manutenção-Service:     http://localhost:8003/graphql"
echo "--------------------------------------------------------"
echo "💡 Para visualizar os logs: $DOCKER_COMPOSE_CMD logs -f"
echo "💡 Para parar os serviços:  $DOCKER_COMPOSE_CMD down"
