This is a simple project that uses FastApi and Uvicorn as the server, and the Ruff formatter and linter.

You need python 3 (done with python 3.13) and Postgres 16

Make sure you have python 3
https://www.python.org/downloads/

You must have postgres 16 installed.
https://www.postgresql.org/download/
Add the lib and bin path of postgres to the PATH environment variable.
For the database, the default server (PostgreSQL 16) was used to store the database.

You must also have poetry installed, which requires pipx.
https://pipx.pypa.io/stable/installation/
When prompt, run the command to add the necessary environment variable path (it should appear in the terminal)

`pipx install poetry`
Restart your computer/environment

At the root of this project, run poetry install

You need to create a .env file at the root of the project, based on the env.example.

Run the project with
Run: fastapi dev main.py

The project will create the necessary database, necessary tables and the required data at start up if it doesn't exist

To test the service, you can either use the swagger to test the route at http://127.0.0.1:8000/docs (or the port used)
or a use an api platform like postman to call GET `127.0.0.1:8000/get_client_config/:id`


