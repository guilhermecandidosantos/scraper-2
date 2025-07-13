from fastapi import FastAPI
from controllers import scraper_controller

app = FastAPI()
app.include_router(scraper_controller.router)
