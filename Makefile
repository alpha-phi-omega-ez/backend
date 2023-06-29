init:
	pip3 install -r requirements.txt

clean:
	pystarter clean

run: clean
	python run.py

stresstest: clean
	gunicorn run:app -w 6 --preload --max-requests-jitter 300