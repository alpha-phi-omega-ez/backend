# apoez.org

Backend service for APOEZ's website to display chapter information and run the campus lost and found system.

## Setup

Clone the repository and enter it

```
git clone https://github.com/alpha-phi-omega-ez/backend.git
cd backend
```

### Environment Variables

Create environment variable through a .env file or via the export command

```
SECRET_KEY = "<random-string>" # for testing/development a random one will automatically be generated
GOOGLE_CLIENT_ID="<google-client-id>" # for google login
GOOGLE_CLIENT_SECRET="<google-client-secret>" # for google login
TESTING="True" # set for testing true or false
SENTRY_DSN="<sentry-dsn>" # for tracing and reporting on errors
```

The Config type can be changed to match the environment it is being run in, with the current options being TestingConfig and ProductionConfig.

### Requirements

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) to install needed libraries

```
uv sync
```

### Run the service

The server will auto-reload on changes to make it easier to develop and test.

```
make develop
```

or

```
uv run fastapi dev --port 9000
```

# Linting and formatting

This project uses ruff for linting in pull requests via github actions, it is recommended that you run format with ruff and/or install ruff in VSCode of your code editor and setup editor formatting using ruff.

Lint
```bash
ruff check server
```

Format
```bash
ruff format server
```

## Authors

- [**Rafael Cenzano**](https://github.com/RafaelCenzano)

## License

This project is licensed under the GNU Affero Public License - see the [LICENSE](LICENSE) file for details
