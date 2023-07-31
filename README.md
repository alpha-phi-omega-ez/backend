# apoez.org

Simple chapter website to display chapter information and run the campus lost and found system.

## Setup

Clone the repository and enter it

```
git clone https://github.com/alpha-phi-omega-ez/apoez.org-flask.git
cd apoez.org-flask
```

### Requirements

Use pip to install needed libraries

```
make
```

or

```
pip install -r requirements.txt
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
