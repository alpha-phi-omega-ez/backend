init:
	pip3 install -r requirements.txt

clean:
	pystarter clean

develop: clean
	python3 main.py

start_db:
	mongod --dbpath db/data --logpath db/logs/mongodb.log

start_db_fork:
	mongod --dbpath db/data --logpath db/logs/mongodb.log --fork
