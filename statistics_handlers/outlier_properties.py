import pandas as pd
from sqlalchemy.orm import Session
from pydantic_models.property import PaginatedResponse, PropertyQueryParams, PropertyResponse
from sqlalchemy_schemas.property import Property, filter_property_query
from utils.dataframe import sanitize_pandas_dataframe


def fetch_filtered_property_outliers_on_price(query_params:PropertyQueryParams, pagination: tuple[int, int], db_session:Session) -> PaginatedResponse:
    
    query = filter_property_query(query_params=query_params, db_session=db_session)
    query = query.filter(Property.is_valid == True)
    query = query.filter(Property.squarefeet > 0)

    df = pd.read_sql(query.statement, db_session.bind).drop_duplicates(subset=['propertyid'], keep='last')

    if df.empty:
        raise ValueError("No data available for the given query parameters.")

    prices = df['price']

    p25_price = prices.quantile(0.25)
    p75_price = prices.quantile(0.75)
    iqr_price = p75_price - p25_price

    # calculate outliers
    lower_bound_price = p25_price - 1.5 * iqr_price
    upper_bound_price = p75_price + 1.5 * iqr_price
    outliers = df[(prices < lower_bound_price) | (prices > upper_bound_price)]

    # pagination
    page = pagination[0]
    page_size = pagination[1]
    total_outliers = len(outliers)
    outliers_paginated = outliers.iloc[(page - 1) * page_size: page * page_size]
    sanitized_records = sanitize_pandas_dataframe(outliers_paginated)
    db_session.close()
    return PaginatedResponse(
        page=pagination[0],
        page_size=pagination[1],
        total=total_outliers,
        results=[PropertyResponse(**item) for item in sanitized_records]
    )


def fetch_filtered_property_outliers_on_price_per_squarefeet(query_params:PropertyQueryParams, pagination: tuple[int, int], db_session:Session) -> PaginatedResponse:
    
    query = filter_property_query(query_params=query_params, db_session=db_session)
    query = query.filter(Property.is_valid == True)
    query = query.filter(Property.squarefeet > 0)

    # Read the prices and squarefeet columns
    df = pd.read_sql(query.statement, db_session.bind).drop_duplicates(subset=['propertyid'], keep='last')

    if df.empty:
        raise ValueError("No data available for the given query parameters.")

    prices = df['price']
    squarefeet = df['squarefeet']
    price_per_sqft = prices / squarefeet

    # calculate metrics for outliers
    p25_pps = price_per_sqft.quantile(0.25)
    p75_pps = price_per_sqft.quantile(0.75)
    iqr_pps = p75_pps - p25_pps

    lower_bound_pps = p25_pps - 1.5 * iqr_pps
    upper_bound_pps = p75_pps + 1.5 * iqr_pps
    outliers = df[(price_per_sqft < lower_bound_pps) | (price_per_sqft > upper_bound_pps)]

    page = pagination[0]
    page_size = pagination[1]
    
    total_outliers = len(outliers)
    outliers_paginated = outliers.iloc[(page - 1) * page_size: page * page_size]
    sanitized_records = sanitize_pandas_dataframe(outliers_paginated)
    db_session.close()
    return PaginatedResponse(
        page=pagination[0],
        page_size=pagination[1],
        total=total_outliers,
        results=[PropertyResponse(**item) for item in sanitized_records]
    )