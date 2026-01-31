This file contains python specific actions to follow and variables to use.

DOCTEST="use doctests"
TESTING="use pytest"

use pyproject.toml > pyproject.ini, unless the project already has the pyproject.ini committed into version control

prefer hypothesis to atheris unless the project is exclusively intended for windows or linux systems
