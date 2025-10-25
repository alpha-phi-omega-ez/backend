init:
	uv sync

develop:
	uv run fastapi dev --port 9000

start_db:
	mongod --dbpath db/data --logpath db/logs/mongodb.log

start_db_fork:
	mongod --dbpath db/data --logpath db/logs/mongodb.log --fork
