import sys

using_docker = '{{ cookiecutter.use_docker }}' == 'y'
using_postgres = '{{ cookiecutter.database }}' == 'postgres'

if using_docker and not using_postgres:
    print("ERROR: Docker set up requires using postgres! It will run in a docker container.")
    sys.exit(1)
