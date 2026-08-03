.PHONY: start stop logs status demo

start:
	./start.sh

demo:
	python3 run_local_demo.py

stop:
	docker compose down || docker-compose down

logs:
	docker compose logs -f || docker-compose logs -f

status:
	docker compose ps || docker-compose ps
