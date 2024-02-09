from fastapi import FastAPI
from map_scraper.fastapi import use_map_scraper


app = FastAPI()
use_map_scraper(app)
