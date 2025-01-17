# apoez.org

Backend service for APOEZ's website to display chapter information and run the campus lost and found system.

## Setup

Clone the repository and enter it

```
git clone https://github.com/alpha-phi-omega-ez/backend.git
cd backend
```

### Environment Variables

Create environment variable through a .env file or other methods

```
SECRET_KEY = "[[RANDOM STRING]]" # for testing/development a random one will automatically be generated
CONFIG = "config.TestingConfig"
```

The Config type can be changed to match the environment it is being run in, with the current options being TestingConfig and ProductionConfig.

### Requirements

Use uv to install needed libraries

```
uv install
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

## Authors

- [**Rafael Cenzano**](https://github.com/RafaelCenzano)

## License

This project is licensed under the GNU Public License - see the [LICENSE](LICENSE) file for details
