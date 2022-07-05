config ?= compile

run:
	docker-compose up --build --remove-orphans

run-d:
	docker-compose up --build --remove-orphans -d

stop:
	docker-compose stop

logs:
	docker-compose logs -f --tail 50

exec:
	docker-compose exec api bash

dev:
	docker-compose -f docker-compose.dev.yml up --build --remove-orphans
