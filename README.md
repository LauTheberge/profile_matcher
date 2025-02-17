This is a simple project that uses FastApi and Uvicorn as the server, and the Ruff formatter and linter.
It runs in local only (no dockerfile)

You need python 3 (done with python 3.13) and Postgres 16

Make sure you have python 3
https://www.python.org/downloads/

You must have postgres 16 installed.
https://www.postgresql.org/download/ .
</br>
Add the lib and bin path of postgres to the PATH environment variable.
</br>
For the database, the default server (PostgreSQL 16) was used to store the database.

You must also have poetry installed, which requires pipx. </br>
https://pipx.pypa.io/stable/installation/ </br>
For example under windows: </br>
`python -m pip install --user pipx` </br>
`python -m pipx ensurepath` </br>
Restart your computer/environment </br>
After that:
`pipx install poetry`

At the root of this project, open a terminal, </br>
create a venv :  </br>
`python -m venv .venv` </br>
navigate to the venv and activate it </br>
`.venv\Scripts\Activate.ps1` </br>
(you might need the terminal to be admin and, under windows, run `Set-ExecutionPolicy RemoteSigned`, run
`Set-ExecutionPolicy Restricted` when done) </br>
run`poetry instal` in the activated venv </br>

IMPORTANT: You need to create a .env file at the root of the project, based on the .env.example.

Once everything is installed, run the project with
`fastapi dev main.py` </br>

The project will create the necessary database, necessary tables and the required data at start up if it doesn't exist

To test the service, you can either use the swagger to test the route at http://127.0.0.1:8000/docs (or the port used)
or a use an api platform like postman to call GET `127.0.0.1:8000/get_client_config/:id`

Note: Despite the small size of the project, the file architecture has been done with the maintenance of a larger 
project in mind.


