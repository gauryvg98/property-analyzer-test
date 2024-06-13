
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from db.sqlite_setup import fetch_db_session
from pydantic_models.property import PropertyQueryParams, property_query_params
from visualizations.property_visualizer import bedrooms_distribution, price_distribution

visualization_router = APIRouter()

@visualization_router.get("/", response_class=HTMLResponse)
def get_visulization_html_page():
    with open("static/visualization.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@visualization_router.get("/property/price/", response_class=HTMLResponse)
def get_price_distribution_visualization(
    query_params:PropertyQueryParams = Depends(property_query_params),
    db_session: Session = Depends(fetch_db_session)
):
    html_plot = price_distribution(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)

@visualization_router.get("/property/rooms/", response_class=HTMLResponse)
def get_statistics(
        query_params:PropertyQueryParams = Depends(property_query_params),
        db_session: Session = Depends(fetch_db_session)
    ):
    html_plot = bedrooms_distribution(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)