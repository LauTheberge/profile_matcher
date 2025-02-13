import uvicorn
from fastapi import FastAPI

from app.app import app

mainApp = FastAPI()
mainApp.mount("/app", app)  # your app routes will now be /app/{your-route-here}


if __name__ == "__main__":
    uvicorn.run(mainApp, host="0.0.0.0", log_level="info")