This uses Postgres 16 as a database, with FastApi and Uvicorn as the server.
This is a simple project that uses the Ruff formatter and linter.
Run poetry install to install the dependencies from the .venv file

Set postgres:
You must hve postgres 16 installed.
Add the lib and bin path of postgres to the PATH environment variable.

postgres 16 comes with pgAdmin 4, which is a GUI for postgres, it is the easiest way to create the database.
Create a server in pgAdmin 4, with these information : 

```
Name = "TechTest",
user = "postgres",
host= '127.0.0.1',
password = "1234", - note this is only for the test purpose (usually, would be secured and not be stored in the code)
port = 5432
```

create a database in the server with the name `TestDatabase`


