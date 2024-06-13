from pydantic import BaseModel


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