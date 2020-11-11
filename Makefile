

setup:
	@python3 -m pip install tox

test: clean setup
	@tox

integration-tests: clean setup
	@tox -e integration

clean:
	@find . -type d -name ".tox" -prune -exec rm -rf {} \;
	@find . -type d -name "*.egg-info" -prune -exec rm -rf {} \;
	@find . -type d -name "*pycache*" -prune -exec rm -rf {} \;
	@find . -type d -name ".pytest_cache" -prune -exec rm -rf {} \;
	@find . -type d -name ".venv" -prune -exec rm -rf {} \;
	@find . -type d -name "build" -prune -exec rm -rf {} \;
	@find . -type d -name "dist" -prune -exec rm -rf {} \;
	@find . -type d -name ".mypy_cache" -prune -exec rm -rf {} \;
	@find . -type f -name ".coverage.*" -prune -exec rm -rf {} \;
	@find . -type f -name ".coverage" -prune -exec rm -rf {} \;
	@find . -type f -name ".DS_Store" -prune -exec rm -rf {} \;

install: clean setup
	@python3 -m venv .venv
	@.venv/bin/python setup.py install

docker_build: clean
	@docker build -t myscript .

docker_run: docker_build
	@docker run myscript
