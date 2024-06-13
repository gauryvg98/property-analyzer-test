from datetime import datetime
from fastapi import Query
from pydantic import BaseModel
from typing import Optional

class PropertyResponse(BaseModel):
    propertyid: int
    address: str
    city : str
    state : str
    zipcode: str
    price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    squarefeet: Optional[float] = None
    datelisted: Optional[datetime] = None

class PaginatedResponse(BaseModel):
    total: int = 0
    page: int
    page_size: int
    results: list[PropertyResponse] = []

class PropertyQueryParams(BaseModel):
    price_min: Optional[float] = Query(None)
    price_max: Optional[float] = Query(None)
    squarefeet_min: Optional[float] = Query(None),
    squarefeet_max: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None)
    bathrooms: Optional[float] = Query(None)
    zipcode: Optional[str] = Query(None)
    city: Optional[str] = Query(None)
    state: Optional[str] = Query(None)

class Percentiles(BaseModel):
    percentile_25_price: float
    percentile_50_price: float
    percentile_75_price: float
    percentile_90_price: float
    percentile_99_price: float

class PropertyStatisticsResponse(BaseModel):
    average_price: float
    median_price: float
    average_price_per_sqft: float
    total_properties: int
    percentiles: Percentiles
    outlier_properties_count: int

def property_query_params(
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    squarefeet_min: Optional[float] = Query(None),
    squarefeet_max: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None),
    bathrooms: Optional[float] = Query(None),
    zipcode: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
) -> PropertyQueryParams:
    return PropertyQueryParams(
        price_min=price_min,
        price_max=price_max,
        squarefeet_min=squarefeet_min,
        squarefeet_max=squarefeet_max,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        zipcode=zipcode,
        city=city,
        state=state,
    )