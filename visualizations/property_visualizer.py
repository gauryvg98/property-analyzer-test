import pandas as pd
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from sqlalchemy_schemas.property import Property, filter_property_query
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px

def price_distribution(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session)
    result = query.all()
    prices = [property.price for property in result]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Histogram(x=prices, nbinsx=50, marker_color='blue', opacity=0.7), row=1, col=1)
    fig.update_layout(title_text='Distribution of Property Prices', xaxis_title='Price', yaxis_title='Frequency')
    db_session.close()
    return fig.to_html(full_html=False)

def bedrooms_distribution(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session).filter(Property.is_valid == True, Property.bedrooms != None, Property.bedrooms > 0).all()
    bedrooms = [property.bedrooms for property in query]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Bar(x=pd.Series(bedrooms).value_counts().sort_index().index, 
                         y=pd.Series(bedrooms).value_counts().sort_index().values, 
                         marker_color='green', opacity=0.7), row=1, col=1)
    fig.update_layout(title_text='Distribution of Properties by Number of Bedrooms', 
                      xaxis_title='Number of Bedrooms', yaxis_title='Frequency')
    db_session.close()
    return fig.to_html(full_html=False)

def price_vs_zipcode_scatter_plot(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session, columns=[Property.price, Property.zipcode, Property.squarefeet]).filter(Property.is_valid == True, Property.squarefeet > 0).all()
    #df = pd.read_sql(query.statement, db_session.bind)
    df = pd.DataFrame(query, columns=["price", "zipcode", "squarefeet"])
    df["price_per_sqft"] = df["price"] / df["squarefeet"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df["zipcode"],
            y=df["price"],
            mode='markers',
            name='Price',
            marker=dict(color='blue', opacity=0.7)
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["zipcode"],
            y=df["price_per_sqft"],
            mode='markers',
            name='Price per Sq.Ft',
            marker=dict(color='red', opacity=0.7)
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title='Scatter Plot of Price and Price per Sq.Ft vs Zipcode',
        xaxis_title='Zipcode',
        yaxis_title='Price',
        yaxis2_title='Price per Sq.Ft',
        xaxis=dict(type='category')
    )
    db_session.close()
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def price_heatmap_zipcode(db_session: Session):
    # Fetch the data from the database
    query = filter_property_query(query_params=None, db_session=db_session, columns=[Property.price, Property.zipcode, Property.squarefeet]).filter(Property.zipcode != None, Property.city == 'Miami', Property.squarefeet > 0).all()
    
    # Check if data is empty
    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    # Create DataFrame
    df = pd.DataFrame(query, columns=["price", "zipcode", "squarefeet"])
    df["price_per_sqft"] = df["price"] / df["squarefeet"]
    # Aggregate data by zipcode
    zipcode_data = df.groupby("zipcode").agg(
        average_price=("price", "mean"),
        number_of_listings=("price", "size")
    ).reset_index()

    # Create price range categories
    bins = [0, 100000, 300000, 500000, 700000, 1000000, float("inf")]
    labels = ["<100k", "100k-300k", "300k-500k", "500k-700k", "700k-1M", ">1M"]
    zipcode_data['price_range'] = pd.cut(zipcode_data['average_price'], bins=bins, labels=labels, right=False)

    # Miami-Dade GeoJSON URL
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
        title="Average Property Price by Zipcode in Miami"
    )

    fig_price.update_geos(fitbounds="locations", visible=False)

    # Create the heatmap for number of listings
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

    # Create the heatmap for price ranges
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
    db_session.close()
    return (
        fig_price.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_listings.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_price_range.to_html(full_html=False, include_plotlyjs='cdn')
    )