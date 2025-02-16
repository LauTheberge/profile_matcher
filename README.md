This uses Postgres 16 as a database, with FastApi and Uvicorn as the server.
This is a simple project that uses the Ruff formatter and linter.
Run poetry install to install the dependencies from the .venv file

Set postgres:
You must have postgres 16 installed.
https://www.postgresql.org/download/

Add the lib and bin path of postgres to the PATH environment variable.

For the database, the default server (PostgreSQL 16) was used to store the database.

create a database in the postgres server(under TechTest) with the name `TestDatabase`

At the root of the project, run poetry install

You need to create a .env file at the root of the project, based on the env.example.

Run the project with
Run: fastapi dev main.py

The project will create the necessary database, necessary tables and the required data at start up if it doesn't exist

To test the service, you can either use the swagger to test the route at http://127.0.0.1:8000/docs (or the port used)
or a use an api platform like postman to call GET `127.0.0.1:8000/get_client_config/:id`


