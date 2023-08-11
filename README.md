# apoez.org

Simple chapter website to display chapter information and run the campus lost and found system.

## Setup

Clone the repository and enter it

```
git clone https://github.com/alpha-phi-omega-ez/apoez.org-flask.git
cd apoez.org-flask
```

### Environment Variables

Create environment variable through a .env file or other methods

```
SECRET_KEY = "[[RANDOM STRING]]" # for testing/development a random one will automatically be generated
CONFIG = "config.TestingConfig"
```

The Config type can be changed to match the environment it is being run in. Current options are TestingConfig and ProductionConfig.

### Requirements

Use pip to install needed libraries

```
make
```

or

```
pip install -r requirements.txt
```

### Setup Database

Use the `database_test.py` to create example data and create a sqllite db, production is planned to be utilizing postgres.

```
python database_test.py create
```

If there have been db changes drop the tables and recreate the tables. Once things are more finalized alembic and flask-migrate will be setup to allow for migrations in the production database

```
python database_test.py clear
python database_test.py create
```

### Run for Development

The server will auto-reload on changes to make it easier to develop and test.

```
make develop
```

or

```
python run.py
```

### Run for Production

```
make run
```

or

```
gunicorn run:app -w 6 --preload --max-requests-jitter 300
```


## Authors

* [**Rafael Cenzano**](https://github.com/RafaelCenzano)

## License

This project is licensed under the GNU Public License - see the [LICENSE](LICENSE) file for details
