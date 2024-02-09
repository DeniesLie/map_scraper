from pydantic import BaseModel, confloat


class Coordinates(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)
