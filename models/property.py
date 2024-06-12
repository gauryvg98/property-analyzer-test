from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class PropertyResponse(BaseModel):
    propertyid: int
    address: str
    city : str
    state : str
    zipcode: str
    price: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    squarefeet: Optional[float] = None
    datelisted: datetime