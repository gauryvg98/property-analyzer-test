import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from sqlalchemy_schemas.property import Property, filter_property_query
import plotly.express as px

def percentile_price_distribution(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session, columns=[Property.price]).filter(Property.price > 0).all()
    
    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(query, columns=["price"])

    bins = [0, 100000, 200000, 300000, 400000, 500000, 750000, 1000000, 1500000, 2000000, 3000000, 4000000, 5000000, float("inf")]
    labels = ["<100k", "100k-200k", "200k-300k", "300k-400k", "400k-500k", "500k-750k", "750k-1M", "1M-1.5M", "1.5M-2M", "2M-3M", "3M-4M", "4M-5M", ">5M"]
    
    df['price_bins'] = pd.cut(df['price'], bins=bins, labels=labels, right=False, include_lowest=True)
    
    df['price_bins'] = df['price_bins'].astype(str)
    df_grouped = df.groupby('price_bins').size().reset_index(name='count')
    df_grouped['price_bins'] = pd.Categorical(df_grouped['price_bins'], categories=labels, ordered=True)
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
    bins = [0, 1, 2, 3, 4, 5, 6, float('inf')]
    labels = ['0', '1', '2', '3', '4', '5', '5+']
    df['bedroom_bins'] = pd.cut(df['bedrooms'], bins=bins, labels=labels, right=False)
    #print(df)
    df_grouped = df.groupby('bedroom_bins').sum().reset_index()
    df_grouped['bedroom_bins'] = df_grouped['bedroom_bins'].astype(str)
    df_grouped = df_grouped.sort_values(by='bedroom_bins')
    fig = px.bar(
        df_grouped,
        x="bedroom_bins",
        y="count",
        labels={"bedroom_bins": "Number of Bedrooms", "count": "Count"},
        title="Distribution of Properties Based on Number of Bedrooms",
        category_orders={"bedroom_bins": labels}
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
            columns=[Property.price, Property.datelisted],
            latest=False,
        ).filter(Property.price > 0, Property.datelisted != None).all()
    
    if not query:
        return "<h3>No data available for the given query parameters</h3>"

    df = pd.DataFrame(query, columns=["price", "datelisted"])

    # Convert DateListed to datetime and extract month and year
    df['datelisted'] = pd.to_datetime(df['datelisted'])
    df['year_month'] = df['datelisted'].dt.to_period('M')

    # Calculate the average price per month
    df_grouped = df.groupby('year_month')['price'].mean().reset_index()
    df_grouped['year_month'] = df_grouped['year_month'].dt.to_timestamp()
    df_grouped = df_grouped.sort_values(by='year_month')

    # Create the line plot
    fig = px.line(
        df_grouped,
        x='year_month',
        y='price',
        labels={"year_month": "Date", "price": "Average Price"},
        title="Average Property Price Over Time"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Average Price",
        title="Average Property Price Over Time"
    )

    db_session.close()
    return fig.to_html(full_html=False, include_plotlyjs='cdn')