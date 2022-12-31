install:
	pip3 install .

install-dependencies:
	pip3 install -r requirements.txt

build:
	pip3 install --upgrade build
	python3 -m build .

test:
	python -m unittest discover .
