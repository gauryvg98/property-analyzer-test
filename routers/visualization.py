
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from db.sqlite_setup import fetch_db_session
from pydantic_models.property import PropertyQueryParams, property_query_params
from visualizations import plots, heatmaps
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
    html_plot = plots.percentile_price_distribution(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)

@visualization_router.get("/property/historical-price/", response_class=HTMLResponse)
def get_historical_price_distribution_visualization(
    query_params:PropertyQueryParams = Depends(property_query_params),
    db_session: Session = Depends(fetch_db_session)
):
    html_plot = plots.historical_price_trends(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)

@visualization_router.get("/property/rooms/", response_class=HTMLResponse)
def get_property_room_distribution_visualization(
        query_params:PropertyQueryParams = Depends(property_query_params),
        db_session: Session = Depends(fetch_db_session)
    ):
    html_plot = plots.bedrooms_distribution(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)

@visualization_router.get("/property/price-vs-zipcode-scatter/", response_class=HTMLResponse)
def get_price_zipcode_scatter_plot(
        query_params:PropertyQueryParams = Depends(property_query_params),
        db_session: Session = Depends(fetch_db_session)
    ):
    html_plot = plots.price_vs_zipcode_box_plot(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)

@visualization_router.get("/property/zipcode-heatmaps/", response_class=HTMLResponse)
def get_heatmaps_zipcode(
        query_params:PropertyQueryParams = Depends(property_query_params),
        db_session: Session = Depends(fetch_db_session)
    ):
    html_plot = heatmaps.heatmaps_zipcode(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)

@visualization_router.get("/property/historical-zipcode-heatmaps/", response_class=HTMLResponse)
def get_historical_heatmaps_zipcode(
        query_params:PropertyQueryParams = Depends(property_query_params),
        db_session: Session = Depends(fetch_db_session)
    ):
    html_plot = heatmaps.historical_heatmaps_zipcode(query_params=query_params, db_session=db_session)
    return HTMLResponse(content=html_plot)