from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    email: str
    hashed_password: str
    google_maps_api_key: Optional[str]
    id: int = None