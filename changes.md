# Changes

## Django - 24 Nov 2019

Included Django. The application can now either be started from the command line, using Start.py,
to generate HTML files, or by starting Django which will create pages on demand.

Reason is twofold:
1. Only demanded files are generated, so no need to wait for all of them
2. Django reloads the application when changes are made, so after all changes the effect can be checked immediately

jinja2 is still used for template generation.

