# main.py

import uvicorn
from fastapi import FastAPI

from app import app

# Usually, the configurations would be fetched from a config store, like CONSUL. But for this test,
# everything is set in the env file.

mainApp = FastAPI()
mainApp.mount("/app", app)  # your app routes will now be /app/{your-route-here}


if __name__ == "__main__":
    uvicorn.run(mainApp, host="0.0.0.0", log_level="debug")