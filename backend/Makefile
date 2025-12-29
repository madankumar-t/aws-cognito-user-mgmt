.PHONY: install test build deploy clean

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

build:
	sam build

deploy:
	sam deploy --guided

clean:
	rm -rf .aws-sam/
	rm -rf __pycache__/
	rm -rf src/**/__pycache__/
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 src/ --max-line-length=120 --exclude=__pycache__
	black --check src/

format:
	black src/

