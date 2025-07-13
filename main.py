from fastapi import FastAPI
from controllers import scraper_controller
from services.db.database import create_table

app = FastAPI()

create_table()

app.include_router(scraper_controller.router)
