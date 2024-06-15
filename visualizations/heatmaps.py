import pandas as pd
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from sqlalchemy_schemas.property import Property, filter_property_query
import plotly.express as px
from utils.dataframe import forwardfill_price_for_historical_property_data
import visualizations.constants as constants


def heatmaps_zipcode(query_params: PropertyQueryParams, db_session: Session):
    query = (
        filter_property_query(
            query_params=query_params,
            db_session=db_session,
            columns=[
                Property.price,
                Property.zipcode,
                Property.squarefeet,
                Property.price_per_square_feet,
            ],
        )
        .filter(
            Property.zipcode != None, Property.city == "Miami", Property.squarefeet > 0
        )
        .all()
    )

    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(
        query, columns=["price", "zipcode", "squarefeet", "price_per_square_feet"]
    )
    zipcode_data = (
        df.groupby("zipcode")
        .agg(
            average_price=("price", "mean"),
            number_of_listings=("price", "size"),
            average_price_per_sqft=("price_per_square_feet", "mean"),
            average_area=("squarefeet", "mean"),
        )
        .reset_index()
    )

    zipcode_data["price_range"] = pd.cut(
        zipcode_data["average_price"],
        bins=constants.bins_price,
        labels=constants.labels_price,
        right=False,
    )
    zipcode_data["price_per_squarefeet_range"] = pd.cut(
        zipcode_data["average_price_per_sqft"],
        bins=constants.bins_ppsf,
        labels=constants.labels_ppsf,
        right=False,
    )

    geojson_url = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/fl_florida_zip_codes_geo.min.json"

    # create the heatmap for average price
    fig_price = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="average_price",
        color_continuous_scale="Viridis",
        scope="usa",
        labels={"average_price": "Average Price"},
        title="Average Property Price by Zipcode in Miami",
    )

    fig_price.update_geos(fitbounds="locations", visible=False)

    fig_ppsf = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="average_price_per_sqft",
        color_continuous_scale="Viridis",
        scope="usa",
        labels={"average_price_per_sqft": "Average Price per Sq.Ft"},
        title="Average Property Price Per Sq. Ft. by Zipcode in Miami",
    )

    fig_ppsf.update_geos(fitbounds="locations", visible=False)

    # create heatmap for number of listings
    fig_listings = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="number_of_listings",
        color_continuous_scale="Blues",
        scope="usa",
        labels={"number_of_listings": "Number of Listings"},
        title="Number of Property Listings by Zipcode in Miami",
    )

    fig_listings.update_geos(fitbounds="locations", visible=False)

    # heatmap for avg squarefeet
    zipcode_data["area_range"] = pd.cut(
        zipcode_data["average_area"],
        bins=constants.area_bins,
        labels=constants.area_labels,
        right=False,
    )

    fig_squarefeet = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="area_range",
        color_continuous_scale="Viridis",
        scope="usa",
        labels={"area_range": "Average Area Range"},
        title="Average House Area Ranges by Zipcode in Miami",
    )

    fig_squarefeet.update_geos(fitbounds="locations", visible=False)

    # create heatmap for price ranges
    fig_price_range = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="price_range",
        scope="usa",
        labels={"price_range": "Price Range"},
        title="Property Price Ranges by Zipcode in Miami",
    )

    fig_price_range.update_geos(fitbounds="locations", visible=False)

    fig_ppfs_range = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="price_per_squarefeet_range",
        scope="usa",
        labels={"price_per_squarefeet_range": "Price per Squarefeet Range"},
        title="Property Price Per Sqft Ranges by Zipcode in Miami",
    )

    fig_ppfs_range.update_geos(fitbounds="locations", visible=False)

    db_session.close()
    return (
        fig_price.to_html(full_html=False, include_plotlyjs="cdn")
        + fig_ppsf.to_html(full_html=False, include_plotlyjs="cdn")
        + fig_listings.to_html(full_html=False, include_plotlyjs="cdn")
        + fig_squarefeet.to_html(full_html=False, include_plotlyjs="cdn")
        + fig_price_range.to_html(full_html=False, include_plotlyjs="cdn")
        + fig_ppfs_range.to_html(full_html=False, include_plotlyjs="cdn")
    )


def historical_heatmaps_zipcode(query_params: PropertyQueryParams, db_session: Session):
    query = (
        filter_property_query(
            query_params=query_params,
            db_session=db_session,
            columns=[
                Property.propertyid,
                Property.price,
                Property.zipcode,
                Property.squarefeet,
                Property.datelisted,
                Property.price_per_square_feet,
            ],
            latest=False,
        )
        .filter(
            Property.zipcode != None,
            Property.squarefeet > 0,
            Property.price > 0,
            Property.datelisted != None,
        )
        .all()
    )

    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(
        query,
        columns=[
            "propertyid",
            "price",
            "zipcode",
            "squarefeet",
            "datelisted",
            "price_per_square_feet",
        ],
    )

    df = forwardfill_price_for_historical_property_data(df=df)

    zipcode_data = (
        df.groupby(["zipcode", "datelisted"])
        .agg(
            average_price=("price", "mean"),
            number_of_listings=("price", "size"),
            average_price_per_sqft=("price_per_square_feet", "mean"),
            average_area=("squarefeet", "mean"),
        )
        .reset_index()
    )

    zipcode_data = zipcode_data.sort_values(by="datelisted")

    zipcode_data["price_range"] = pd.cut(
        zipcode_data["average_price"],
        bins=constants.bins_price,
        labels=constants.labels_price,
        right=False,
    )
    zipcode_data["price_per_squarefeet_range"] = pd.cut(
        zipcode_data["average_price_per_sqft"],
        bins=constants.bins_ppsf,
        labels=constants.labels_ppsf,
        right=False,
    )

    geojson_url = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/fl_florida_zip_codes_geo.min.json"

    # create the heatmap for average price
    fig_price = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="average_price",
        color_continuous_scale="Viridis",
        scope="usa",
        labels={"average_price": "Average Price"},
        title="Average Property Price by Zipcode in Miami",
        animation_frame="datelisted",
    )

    fig_price.update_geos(fitbounds="locations", visible=False)

    # create the heatmap for average price per square feet
    fig_ppsf = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="average_price_per_sqft",
        color_continuous_scale="Viridis",
        scope="usa",
        labels={"average_price_per_sqft": "Average Price per Sq.Ft"},
        title="Average Property Price Per Sq. Ft. by Zipcode in Miami",
        animation_frame="datelisted",
    )

    fig_ppsf.update_geos(fitbounds="locations", visible=False)

    # create heatmap for number of listings
    fig_listings = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="number_of_listings",
        color_continuous_scale="Blues",
        scope="usa",
        labels={"number_of_listings": "Number of Listings"},
        title="Number of Property Listings by Zipcode in Miami",
        animation_frame="datelisted",
    )

    fig_listings.update_geos(fitbounds="locations", visible=False)

    db_session.close()
    return (
        fig_price.to_html(full_html=False, include_plotlyjs="cdn")
        + fig_ppsf.to_html(full_html=False, include_plotlyjs="cdn")
        + fig_listings.to_html(full_html=False, include_plotlyjs="cdn")
    )
