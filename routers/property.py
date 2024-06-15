from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.sqlite_setup import fetch_db_session
from middleware.pagination import PageRequest, pagination_params
from pydantic_models.property import (
    PaginatedResponse,
    PropertyQueryParams,
    property_query_params,
)
from pydantic_models.statistics import PropertyStatisticsResponse
from sqlalchemy_schemas.property import filter_properties
from statistics_handlers.outlier_properties import (
    fetch_filtered_property_outliers_on_price,
    fetch_filtered_property_outliers_on_price_per_squarefeet,
)
from statistics_handlers.stats import calculate_property_statistics

property_router = APIRouter()


@property_router.get("/", response_model=PaginatedResponse)
def get_properties(
    query_params: PropertyQueryParams = Depends(property_query_params),
    pagination: PageRequest = Depends(pagination_params),
    db_session: Session = Depends(fetch_db_session),
):
    properties: PaginatedResponse = filter_properties(
        query_params=query_params, pagination=pagination, db_session=db_session
    )

    return properties


@property_router.get("/statistics/", response_model=PropertyStatisticsResponse)
def get_statistics(
    query_params: PropertyQueryParams = Depends(property_query_params),
    db_session: Session = Depends(fetch_db_session),
):
    stats: PropertyStatisticsResponse = calculate_property_statistics(
        query_params=query_params, db_session=db_session
    )
    return stats


@property_router.get("/outliers/price/", response_model=PaginatedResponse)
def get_outliers_on_price(
    query_params: PropertyQueryParams = Depends(property_query_params),
    pagination: PageRequest = Depends(pagination_params),
    db_session: Session = Depends(fetch_db_session),
):
    page_response: PaginatedResponse = fetch_filtered_property_outliers_on_price(
        query_params=query_params, pagination=pagination, db_session=db_session
    )
    return page_response


@property_router.get(
    "/outliers/price-per-squarefeet/", response_model=PaginatedResponse
)
def get_outliers_on_price_per_squarefeet(
    query_params: PropertyQueryParams = Depends(property_query_params),
    pagination: PageRequest = Depends(pagination_params),
    db_session: Session = Depends(fetch_db_session),
):
    page_response: PaginatedResponse = (
        fetch_filtered_property_outliers_on_price_per_squarefeet(
            query_params=query_params, pagination=pagination, db_session=db_session
        )
    )
    return page_response
