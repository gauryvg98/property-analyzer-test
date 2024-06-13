
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.sqlite_setup import fetch_db_session
from pydantic_models.property import PropertyQueryParams, property_query_params
from visualizations.property_visualizer import bedrooms_distribution, price_distribution

visualization_router = APIRouter()

@visualization_router.get("/property/price/")
def get_price_distribution_visualization(
    query_params:PropertyQueryParams = Depends(property_query_params),
    db_session: Session = Depends(fetch_db_session)
):
    html_plot = bedrooms_distribution(query_params=query_params, db_session=db_session)
    return html_plot

@visualization_router.get("/property/rooms/")
def get_statistics(
        query_params:PropertyQueryParams = Depends(property_query_params),
        db_session: Session = Depends(fetch_db_session)
    ):
    html_plot = price_distribution(query_params=query_params, db_session=db_session)
    return html_plot