import pandas as pd
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from sqlalchemy_schemas.property import Property, filter_property_query
import plotly.express as px

def heatmaps_zipcode(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(
                        query_params=query_params, db_session=db_session, 
                        columns=[Property.price, Property.zipcode, Property.squarefeet, Property.price_per_square_feet]
                    ).filter(
                        Property.zipcode != None, Property.city == 'Miami', Property.squarefeet > 0
                    ).all()
    
    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(query, columns=["price", "zipcode", "squarefeet", "price_per_square_feet"])
    zipcode_data = df.groupby("zipcode").agg(
        average_price=("price", "mean"),
        number_of_listings=("price", "size"),
        average_price_per_sqft=("price_per_square_feet", "mean"),
        average_area=("squarefeet", "mean"),
    ).reset_index()

    bins_price = [0, 100000, 300000, 500000, 700000, 1000000, 2000000, 4000000, float("inf")]
    labels_price = ["<100k", "100k-300k", "300k-500k", "500k-700k", "700k-1M", "1M-2M", "2M-4M", ">4M"]

    bins_ppsf = [0, 100, 200, 300, 400, 500, 600, 800, 1000, 1200, 1600, float("inf")]
    labels_ppsf = ["<100", "100-200", "200-300", "300-400", "400-500", "500-600", "600-800", "800-1000", "1000-1200", "1200-1600", ">1600"]
    
    zipcode_data['price_range'] = pd.cut(zipcode_data['average_price'], bins=bins_price, labels=labels_price, right=False)
    zipcode_data['price_per_squarefeet_range'] = pd.cut(zipcode_data['average_price_per_sqft'], bins=bins_ppsf, labels=labels_ppsf, right=False)

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
        title="Average Property Price by Zipcode in Miami"
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
        title="Average Property Price Per Sq. Ft. by Zipcode in Miami"
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
        title="Number of Property Listings by Zipcode in Miami"
    )

    fig_listings.update_geos(fitbounds="locations", visible=False)

    # heatmap for avg squarefeet
    area_bins = [0, 1000, 2000, 3000, 4000, 5000, float("inf")]
    area_labels = ["<1000", "1000-2000", "2000-3000", "3000-4000", "4000-5000", ">5000"]
    zipcode_data['area_range'] = pd.cut(zipcode_data['average_area'], bins=area_bins, labels=area_labels, right=False)

    fig_squarefeet = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="area_range",
        color_continuous_scale="Viridis",
        scope="usa",
        labels={"area_range": "Average Area Range"},
        title="Average House Area Ranges by Zipcode in Miami"
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
        title="Property Price Ranges by Zipcode in Miami"
    )

    fig_price_range.update_geos(fitbounds="locations", visible=False)

    fig_ppfs_range = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="price_per_squarefeet_range",
        scope="usa",
        labels={"price_per_squarefeet_range":"Price per Squarefeet Range"},
        title="Property Price Per Sqft Ranges by Zipcode in Miami"
    )

    fig_ppfs_range.update_geos(fitbounds="locations", visible=False)

    db_session.close()
    return (
        fig_price.to_html(full_html=False, include_plotlyjs='cdn') + 
        fig_listings.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_squarefeet.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_price_range.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_ppfs_range.to_html(full_html=False, include_plotlyjs='cdn')
    )

def historical_heatmaps_zipcode(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(
            query_params=query_params, db_session=db_session, 
            columns=[Property.propertyid, Property.price, Property.zipcode, Property.squarefeet, Property.datelisted, Property.price_per_square_feet],
            latest=False,
        ).filter(
            Property.zipcode != None, Property.squarefeet > 0, Property.price > 0, Property.datelisted != None
        ).all()
    
    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(query, columns=["propertyid", "price", "zipcode", "squarefeet", "datelisted", "price_per_square_feet"])
    df['datelisted'] = pd.to_datetime(df['datelisted']).dt.to_period('M')
    
    # all_periods = pd.period_range(start=df['datelisted'].min(), end=df['datelisted'].max(), freq='M')
    # all_propertyids = df['propertyid'].unique()
    # complete_index = pd.MultiIndex.from_product([all_propertyids, all_periods], names=['propertyid', 'datelisted'])
    # df.set_index(['propertyid', 'datelisted'], inplace=True)
    # df = df.reset_index().drop_duplicates(subset=['propertyid', 'datelisted']).set_index(['propertyid', 'datelisted'])
    # df = df.reindex(complete_index).sort_index()
    # df = df.groupby('propertyid').ffill().reset_index()
    # print(df)

    zipcode_data = df.groupby(["zipcode", "datelisted"]).agg(
        average_price=("price", "mean"),
        number_of_listings=("price", "size"),
        average_price_per_sqft=("price_per_square_feet", "mean"),
        average_area=("squarefeet", "mean"),
    ).reset_index()

    zipcode_data = zipcode_data.sort_values(by='datelisted')

    bins_price = [0, 100000, 300000, 500000, 700000, 1000000, 2000000, 4000000, float("inf")]
    labels_price = ["<100k", "100k-300k", "300k-500k", "500k-700k", "700k-1M", "1M-2M", "2M-4M", ">4M"]

    bins_ppsf = [0, 100, 200, 300, 400, 500, 600, 800, 1000, 1200, 1600, float("inf")]
    labels_ppsf = ["<100", "100-200", "200-300", "300-400", "400-500", "500-600", "600-800", "800-1000", "1000-1200", "1200-1600", ">1600"]
    
    zipcode_data['price_range'] = pd.cut(zipcode_data['average_price'], bins=bins_price, labels=labels_price, right=False)
    zipcode_data['price_per_squarefeet_range'] = pd.cut(zipcode_data['average_price_per_sqft'], bins=bins_ppsf, labels=labels_ppsf, right=False)

    geojson_url = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/fl_florida_zip_codes_geo.min.json"

    # Create the heatmap for average price
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
        animation_frame="datelisted"
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
        animation_frame="datelisted"
    )

    fig_ppsf.update_geos(fitbounds="locations", visible=False)

    # Create heatmap for number of listings
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
        animation_frame="datelisted"
    )

    fig_listings.update_geos(fitbounds="locations", visible=False)

    # Heatmap for avg squarefeet
    area_bins = [0, 1000, 2000, 3000, 4000, 5000, float("inf")]
    area_labels = ["<1000", "1000-2000", "2000-3000", "3000-4000", "4000-5000", ">5000"]
    zipcode_data['area_range'] = pd.cut(zipcode_data['average_area'], bins=area_bins, labels=area_labels, right=False)

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
        animation_frame="datelisted"
    )

    fig_squarefeet.update_geos(fitbounds="locations", visible=False)

    # Create heatmap for price ranges
    fig_price_range = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="price_range",
        scope="usa",
        labels={"price_range": "Price Range"},
        title="Property Price Ranges by Zipcode in Miami",
        animation_frame="datelisted"
    )

    fig_price_range.update_geos(fitbounds="locations", visible=False)

    fig_ppfs_range = px.choropleth(
        zipcode_data,
        geojson=geojson_url,
        locations="zipcode",
        featureidkey="properties.ZCTA5CE10",
        color="price_per_squarefeet_range",
        scope="usa",
        labels={"price_per_squarefeet_range":"Price per Squarefeet Range"},
        title="Property Price per Sq.Ft. Ranges by Zipcode in Miami",
        animation_frame="datelisted"
    )

    fig_ppfs_range.update_geos(fitbounds="locations", visible=False)

    db_session.close()
    return (
        fig_price.to_html(full_html=False, include_plotlyjs='cdn') + 
        fig_listings.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_squarefeet.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_price_range.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_ppfs_range.to_html(full_html=False, include_plotlyjs='cdn')
    )