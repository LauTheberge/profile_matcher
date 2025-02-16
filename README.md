This uses Postgres 16 as a database, with FastApi and Uvicorn as the server.
This is a simple project that uses the Ruff formatter and linter.
Run poetry install to install the dependencies from the .venv file

Set postgres:
You must have postgres 16 installed.
https://www.postgresql.org/download/

Add the lib and bin path of postgres to the PATH environment variable.

postgres 16 comes with pgAdmin 4, which is a GUI for postgres, it is an easy way to create the database.
Create a server in pgAdmin 4, with these information : 

```
Name = "TechTest",
user = "postgres",
host= '127.0.0.1',
password = "1234", - note this is only for the test purpose (usually, would be secured and not be stored in the code)
port = 5432
```

create a database in the postgres server(under TechTest) with the name `TestDatabase`

At the root of the project, run poetry install

You need to create a .env file at the root of the project, based on the env.example.

Run the project with
Run: fastapi dev main.py

The project will create the necessary tables and the required data at start up

To test the service, you can either use the 


