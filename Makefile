include .env
compose = docker compose
lines?=all


build:
	sudo $(compose) up --build -d

logs:
	sudo $(compose) logs -f --tail=$(lines)

stop:
	sudo $(compose) stop

ps:
	sudo $(compose) ps

down:
	sudo $(compose) down

admin:
	sudo $(compose) exec app ./manage.py createsuperuser
app-build:
	sudo $(compose) up --build -d app
app-logs:
	sudo $(compose) logs --tail $(lines)  -f app
app-stop:
	sudo $(compose) stop app

mongo-shell:
	sudo $(compose) exec db mongo
mongo-build:
	sudo $(compose) up -d db
mongo-logs:
	sudo $(compose) logs --tail $(lines) -f db
mongo-stop:
	sudo $(compose) stop db
mongo-restore:
	sudo $(compose) exec db mongorestore -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD} /dumps/
