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


# Run to generate HTML reports

    $ python3 Start.py

or

    $ python3
    >>> import Start
    >>> Start.main()

# Run from Django

    ./server $ python3 manage.py runserver
