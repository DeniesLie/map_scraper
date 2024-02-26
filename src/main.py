import logging.config
import json
import pathlib
from fastapi import FastAPI
from map_scraper.fastapi import use_map_scraper
import os


if not os.path.exists("logs"):
    os.makedirs("logs")
log_config_path = pathlib.Path('log_config.json')
with open(log_config_path) as log_config_file:
    log_config = json.load(log_config_file)
logging.config.dictConfig(log_config)

app = FastAPI()
use_map_scraper(app)


