# Python Cli Example Starter


This an example of a "properly" packaged python module using the Click library to build a cli tool.


## Setup

* Install Python 3.x (currently latest is 3.9)
* Setup your damn debugger!
    
    Debugging with print statements is for people who don't know better. Just try it out.
    
    Here are some links that will help.
    
    * [vscode](https://code.visualstudio.com/docs/python/testing) - It might be a little frustrating but it's worth it, I promise.
    * [intellij](https://www.jetbrains.com/help/pycharm/part-1-debugging-python-code.html) - My personal favorite. Should just work out of the box.
    * If you're a "real" programmer and only use command line and vim, try [pdb](https://pymotw.com/3/pdb/) (debugging on hard mode) or [ipdb](https://pypi.org/project/ipdb/) for something a little easier. When that doesn't work, see above.


Features
----------

##### Python features
* [click](https://click.palletsprojects.com/en/7.x/) - A powerful library for building command line tools in python
* [click-log](https://click-log.readthedocs.io/en/stable/) - easy logging for click (can sometimes be a pain)
* [setup.py](https://python-packaging.readthedocs.io/en/latest/minimal.html) - an implementation of python packaging (my example maybe a little out of date)
    * [entry_points](https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html) - using python package to install a cli script (used for click)

##### Tests
* [tox](https://tox.readthedocs.io/en/latest/) - a great high-level test runner for python
* [pytest](https://docs.pytest.org/en/stable/) - powerful test library for python
    * [click.testing](https://click.palletsprojects.com/en/7.x/testing/) - testing library for click
    * mocking (using unittest.mock)
    * fixtures
* [pep8](https://pypi.org/project/pep8/) - python style linting
* [mypy](http://mypy-lang.org/) - static type checker for python
* [coverage](https://coverage.readthedocs.io/en/coverage-5.3/) - coverage tool for python
* [flake8](https://flake8.pycqa.org/en/latest/) - style enforcement

##### Tools
* Docker
* make


## Usage

The program must be invoked as follows (we have it scripted, so the format is important). Depending on your language choice, myscript may need to be bash script (or a .bat) that actually invokes your code.

For example:
```shell script
myscript.sh input.csv output.csv
```

## Installing and running the tool

There are several ways you can run the program. 

### Running from your local environment
`make install` will install the `myscript` tool in a python venv in the root
of the project directory `.venv`.

Note: `./myscript` depends on the local `.venv` being present.

```shell script
make install 
./myscript --help
./myscript <input_file> <output_file>
```

### Installing on the system via python

The python installation should install `myscript` too into your path assuming 
that the python `/bin` directory is already in your PATH

```shell script
python setup.py install
myscript --help
myscript <input_file> <output_file>
```

### Running from a docker container.

Note: to run the tool in a docker container, you must copy the input file into 
your current working directory

```shell script
make docker      # This will build your docker container with the tag `myscript` 
cp <input_file> ./   # Copy your input file into working directory
docker run -v$PWD:/app myscript --help
docker run -v$PWD:/app myscript <input_file> <output_file>
```

## Running tests

This project uses `tox` as a test runner. Tests suites involve linting, static code analysis
and commandline interface testing. By default, this will not run tests that involve integration
testing. There is another set of integration tests that will perform tests that will hit
the `/accounts` service endpoint.


### Run all tests except integration tests
```shell script
make test     # run test using local tox
```

Note: This will run linting, code smell tests, and tests that do not hit the account service

### Run integration tests
```shell script
make integration-tests
```


