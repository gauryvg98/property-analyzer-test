from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.sqlite_setup import fetch_db_session
from models import statistics
from schemas.property import Property

property_router = APIRouter()

property_router.api_route("/property")
