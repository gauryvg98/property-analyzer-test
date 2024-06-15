import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from sqlalchemy_schemas.property import Property, filter_property_query
import plotly.express as px
import visualizations.constants as constants
from utils.dataframe import forwardfill_price_for_historical_property_data

def price_distribution(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session, columns=[Property.price]).filter(Property.price > 0).all()
    
    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(query, columns=["price"])
    
    df['price_bins'] = pd.cut(df['price'], bins=constants.bins_price_histogram, labels=constants.labels_price_histogram, right=False, include_lowest=True)
    
    df['price_bins'] = df['price_bins'].astype(str)
    df_grouped = df.groupby('price_bins').size().reset_index(name='count')
    df_grouped['price_bins'] = pd.Categorical(df_grouped['price_bins'], categories=constants.labels_price_histogram, ordered=True)
    df_grouped = df_grouped.sort_values(by='price_bins')
    fig = px.histogram(
        df_grouped,
        x='price_bins',
        y='count',
        labels={"price_bins": "Price Range", "count": "Count"},
        title="Distribution of Property Prices"
    )

    fig.update_layout(
        xaxis_title="Price Range",
        yaxis_title="Count",
        title="Distribution of Property Prices"
    )

    db_session.close()
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def bedrooms_distribution(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session, columns=[Property.bedrooms, func.count(Property.id).label('count')]).filter(Property.bedrooms != None).group_by(Property.bedrooms)
    result = query.all()
    if not query:
        return "<h3>No data available for the given query parameters</h3>"
    df = pd.DataFrame(result, columns=["bedrooms", "count"])

    df['bedroom_bins'] = pd.cut(df['bedrooms'], bins=constants.bins_bedrooms, labels=constants.labels_bedrooms, right=False)
    df_grouped = df.groupby('bedroom_bins').sum().reset_index()
    df_grouped['bedroom_bins'] = df_grouped['bedroom_bins'].astype(str)
    df_grouped = df_grouped.sort_values(by='bedroom_bins')
    fig = px.bar(
        df_grouped,
        x="bedroom_bins",
        y="count",
        labels={"bedroom_bins": "Number of Bedrooms", "count": "Count"},
        title="Distribution of Properties Based on Number of Bedrooms",
        category_orders={"bedroom_bins": constants.labels_bedrooms}
    )

    fig.update_layout(
        xaxis_title="Number of Bedrooms",
        yaxis_title="Count",
        title="Distribution of Properties Based on Number of Bedrooms"
    )

    db_session.close()
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def price_vs_zipcode_box_plot(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session, columns=[Property.price, Property.zipcode, Property.squarefeet, Property.price_per_square_feet]).filter(Property.price > 0, Property.squarefeet > 0).all()
    df = pd.DataFrame(query, columns=["price", "zipcode", "squarefeet", "price_per_square_feet"])
    
    fig_price = px.box(
        df,
        x="zipcode",
        y="price",
        title="Box Plot of Price vs Zipcode",
        labels={"price": "Price", "zipcode": "Zipcode"},
    )

    fig_price.update_layout(
        yaxis_title="Price",
        xaxis_title="Zipcode",
        xaxis=dict(type='category')
    )

    fig_price_per_sqft = px.box(
        df,
        x="zipcode",
        y="price_per_square_feet",
        title="Box Plot of Price per Sq.Ft vs Zipcode",
        labels={"price_per_square_feet": "Price per Sq.Ft", "zipcode": "Zipcode"},
    )

    fig_price_per_sqft.update_layout(
        yaxis_title="Price per Sq.Ft",
        xaxis_title="Zipcode",
        xaxis=dict(type='category')
    )

    db_session.close()
    return (
        fig_price.to_html(full_html=False, include_plotlyjs='cdn') +
        fig_price_per_sqft.to_html(full_html=False, include_plotlyjs='cdn')
    )

def historical_price_trends(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(
            query_params=query_params, 
            db_session=db_session, 
            columns=[Property.propertyid, Property.price, Property.datelisted, Property.price_per_square_feet],
            latest=False,
        ).filter(Property.price > 0, Property.datelisted != None).all()
    
    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(query, columns=["propertyid", "price", "datelisted", "price_per_square_feet"])
    
    df = forwardfill_price_for_historical_property_data(df=df)
    
    df_grouped_price = df.groupby('datelisted')['price'].mean().reset_index()
    df_grouped_price['datelisted'] = df_grouped_price['datelisted'].dt.to_timestamp()
    df_grouped_price = df_grouped_price.sort_values(by='datelisted')

    df_grouped_ppsf = df.groupby('datelisted')['price_per_square_feet'].mean().reset_index()
    df_grouped_ppsf['datelisted'] = df_grouped_ppsf['datelisted'].dt.to_timestamp()
    df_grouped_ppsf = df_grouped_ppsf.sort_values(by='datelisted')
    
    fig_price = px.line(
        df_grouped_price,
        x='datelisted',
        y='price',
        labels={"datelisted": "Date", "price": "Average Price"},
        title="Average Property Price Over Time"
    )

    fig_price.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Price",
        title="Average Property Price Over Time"
    )

    fig_ppsf = px.line(
        df_grouped_ppsf,
        x='datelisted',
        y='price_per_square_feet',
        labels={"datelisted": "Date", "price_per_square_feet": "Average Price Per SqFt"},
        title="Average Property Price Over Time"
    )

    fig_ppsf.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Price Per Squarefeet",
        title="Average Property Price per square feet Over Time"
    )

    db_session.close()
    return (
        fig_price.to_html(full_html=False, include_plotlyjs='cdn') + 
        fig_ppsf.to_html(full_html=False, include_plotlyjs='cdn')
    )
