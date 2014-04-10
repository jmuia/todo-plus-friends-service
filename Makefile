all: debug

test:
	python -m unittest discover -v -t . -s test

debug:
	dev_appserver.py --host 0.0.0.0 .

deploy:
	make test && appcfg.py update --oauth2 .

.PHONY: test debug deploy
