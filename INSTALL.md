# Install

Sweep uses the following python extras:
* sqlite3
* jira-python
* atlassian
* jinja2
* flask
* Flask-Table
* Django
* plotly

You can install them with: pip install <name>

# Configure

1. Copy ./src/sweep.yaml to ./src/../../sweep.yaml
2. Modify the settings in sweep.yaml


# Run

There is no packaged installation, so for now, Sweep is just accessed from the ./src directory.

## Run Jupyter notebook

    .../src $ python3 jupyter lab

Check out [notebook_to_jira.ipynb](notebook_to_jira.ipynb)


## Run to generate HTML reports

    .../src $ python3 Start.py

or

    .../src $ python3
    >>> import Start
    >>> Start.main()

## Run from Django

    .../src/server $ python3 manage.py runserver
