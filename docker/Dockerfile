FROM hdgigante/python-opencv:4.8.1-alpine

COPY . /map_scraper/

WORKDIR /map_scraper
RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /map_scraper/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]