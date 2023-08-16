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

### Run with HTTPS

Extra configuration is necessary to run the server in HTTPS mode. To generate your own certificate files for the server to use, please follow the directions at https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/#how-it-works. This guide also specifies how to get your computer to trust the generated server certificate. Test certificates are also available in the test-certs directory; if these are used, your browser will not trust the server certificate, which must be manually bypassed, but should not affect the website. Run the server with the test certificate with
```
gunicorn --certfile=test-certs/test.crt --keyfile=test-certs/test.key run:app -w 6 --preload --max-requests-jitter 300
```

The server can then be reached at https://localhost:8000.

### Run with OAuth

To test OAuth, you must first run the server in HTTPS mode as above. There are two alternatives. First, you may ask for someone who has created their own test credentials and ask them to add your login email to their credentials and send you the credentials json file.  
If you would like to create your own test credentials, visit https://console.cloud.google.com and sign in with any Google account. Then, go to Select a project -> NEW PROJECT (defaults will work). Then, reselect the project you just created and go to the three horizontal line menu on the top left and select APIs & Services -> Credentials -> Create credentials -> OAuth client ID -> CONFIGURE CONSENT SCREEN. The options necessary are Internal, then whatever; you don't need consent for anything so mostly defaults should work - however, you must also specify all of the emails which are allowed to use the credentials. Once the consent stuff is done, go back to Create OAuth client ID and do Application type = Web application -> Authorized JavaScript origins = http://127.0.0.1:8000 -> Authorized redirect URIs = http://localhost:8000/login/callback , https://localhost:8000/login/callback , http://127.0.0.1:8000/login/callback , and https://127.0.0.1:8000/login/callback. Finally, you can create the credentials and download them as a JSON file or get the details.  

Once you have the credentials json or details, there are two ways to enter them. First, you can add the environment variables of GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET while running the server. Otherwise, you can paste the json file into your user's Documents folder wherever the server is running from and rename it to key.json.  

After this configuration, you should be able to go to https://localhost:8000/login and successfully be redirected to a Google login screen, where you can input one of the emails which is accepted by the test credentials.  

## Authors

* [**Rafael Cenzano**](https://github.com/RafaelCenzano)

## License

This project is licensed under the GNU Public License - see the [LICENSE](LICENSE) file for details
