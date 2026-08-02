.PHONY: start stop logs status

start:
	./start.sh

stop:
	docker compose down || docker-compose down

logs:
	docker compose logs -f || docker-compose logs -f

status:
	docker compose ps || docker-compose ps
