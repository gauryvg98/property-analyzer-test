import pandas as pd
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from pydantic_models.statistics import Percentiles, PropertyStatisticsResponse
from sqlalchemy_schemas.property import Property, filter_property_query


def calculate_property_statistics(query_params: PropertyQueryParams, db_session: Session) -> PropertyStatisticsResponse:
    result = filter_property_query(query_params=query_params, db_session=db_session, columns=[Property.price, Property.price_per_square_feet]).filter(Property.price > 0, Property.price_per_square_feet > 0).all()
    # Read the prices and squarefeet columns
    df = pd.DataFrame(result, columns=["price", "price_per_square_feet"])

    if df.empty:
        raise ValueError("No data available for the given query parameters.")

    prices = df['price']
    ppsf = df['price_per_square_feet']
    # calculate percentiles
    p25 = prices.quantile(0.25)
    p50 = prices.median()
    p75 = prices.quantile(0.75)
    p90 = prices.quantile(0.90)
    p99 = prices.quantile(0.99)
    iqr = p75 - p25

    average_price = prices.mean()
    average_price_per_sqft = ppsf.mean()
    total_properties = len(prices)

    # calculate outliers
    lower_bound = p25 - 1.5 * iqr
    upper_bound = p75 + 1.5 * iqr
    outliers_count = len(df[(prices < lower_bound) | (prices > upper_bound)])
    
    db_session.close()

    return PropertyStatisticsResponse(
        average_price=average_price,
        median_price=p50,
        average_price_per_sqft=average_price_per_sqft,
        total_properties=total_properties,
        percentiles=Percentiles(
            percentile_25_price=p25,
            percentile_50_price=p50,
            percentile_75_price=p75,
            percentile_90_price=p90,
            percentile_99_price=p99,
        ),
        outlier_properties_count=outliers_count,
    )