all: test

test:
	python -m unittest discover -v -t . -s test

test-pypy:
	pypy -m unittest discover -v -t . -s test

debug:
	dev_appserver.py --host 0.0.0.0 .

deploy:
	appcfg.py update .

.PHONY: test test-deps debug deply
