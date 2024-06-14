from datetime import datetime
from fastapi import Query
import pandas as pd
from pydantic import BaseModel
from typing import Optional
from middleware.pagination import PageRequest
from utils.dataframe import sanitize_pandas_dataframe

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
    price_per_square_feet: Optional[float] = None
    datelisted: Optional[datetime] = None

class PaginatedResponse(BaseModel):
    total: int = 0
    page: int
    page_size: int
    results: list[PropertyResponse] = []

class PropertyQueryParams(BaseModel):
    price_min: Optional[float] = Query(None)
    price_max: Optional[float] = Query(None)
    price_per_square_feet_min: Optional[float] = Query(None)
    price_per_square_feet_max: Optional[float] = Query(None)
    squarefeet_min: Optional[float] = Query(None),
    squarefeet_max: Optional[float] = Query(None),
    bedrooms: Optional[int] = Query(None)
    bathrooms: Optional[float] = Query(None)
    zipcode: Optional[str] = Query(None)
    city: Optional[str] = Query(None)
    state: Optional[str] = Query(None)

def property_query_params(
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    price_per_square_feet_min: Optional[float] = Query(None),
    price_per_square_feet_max: Optional[float] = Query(None),
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
        price_per_square_feet_min=price_per_square_feet_min,
        price_per_square_feet_max=price_per_square_feet_max,
        squarefeet_min=squarefeet_min,
        squarefeet_max=squarefeet_max,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        zipcode=zipcode,
        city=city,
        state=state,
    )

def convert_df_to_PropertyResponse(df: pd.DataFrame) -> list[PropertyResponse]:
    dict_list = sanitize_pandas_dataframe(df)
    results=[PropertyResponse(**item) for item in dict_list]
    return results
    