import pandas as pd
from sqlalchemy.orm import Session
from middleware.pagination import PageRequest
from pydantic_models.property import (
    PaginatedResponse,
    PropertyQueryParams,
    convert_df_to_PropertyResponse,
)
from sqlalchemy_schemas.property import Property, filter_property_query
from utils.dataframe import calculate_outliers, sqlalchemy_models_to_dataframe


def fetch_filtered_property_outliers_on_price(
    query_params: PropertyQueryParams, pagination: PageRequest, db_session: Session
) -> PaginatedResponse:

    result = (
        filter_property_query(query_params=query_params, db_session=db_session)
        .filter(Property.price > 0, Property.squarefeet > 0)
        .all()
    )

    df = sqlalchemy_models_to_dataframe(result)

    if df.empty:
        raise ValueError("No data available for the given query parameters.")

    outliers = calculate_outliers(df, df["price"])
    db_session.close()
    return __paginate_outliers_dataframe(outliers, pagination)


def fetch_filtered_property_outliers_on_price_per_squarefeet(
    query_params: PropertyQueryParams, pagination: PageRequest, db_session: Session
) -> PaginatedResponse:

    result = (
        filter_property_query(query_params=query_params, db_session=db_session)
        .filter(Property.price > 0, Property.squarefeet > 0)
        .all()
    )

    df = sqlalchemy_models_to_dataframe(result)

    if df.empty:
        raise ValueError("No data available for the given query parameters.")

    outliers = calculate_outliers(df, df["price_per_square_feet"])
    db_session.close()
    return __paginate_outliers_dataframe(outliers, pagination)


def __paginate_outliers_dataframe(
    outliers: pd.DataFrame, pageRequest: PageRequest
) -> PaginatedResponse:
    page = pageRequest.page
    page_size = pageRequest.page_size
    total_outliers = len(outliers)
    outliers_paginated = outliers.iloc[(page - 1) * page_size : page * page_size]
    return PaginatedResponse(
        page=page,
        page_size=page_size,
        total=total_outliers,
        results=convert_df_to_PropertyResponse(outliers_paginated),
    )
