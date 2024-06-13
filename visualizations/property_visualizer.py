import pandas as pd
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from sqlalchemy_schemas.property import Property, filter_property_query
from plotly.subplots import make_subplots
import plotly.graph_objs as go

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
    query = filter_property_query(query_params=query_params, db_session=db_session)
    query = query.filter(Property.is_valid == True).filter(Property.bedrooms != None, Property.bedrooms > 0)
    result = query.all()
    bedrooms = [property.bedrooms for property in result]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Bar(x=pd.Series(bedrooms).value_counts().sort_index().index, 
                         y=pd.Series(bedrooms).value_counts().sort_index().values, 
                         marker_color='green', opacity=0.7), row=1, col=1)
    fig.update_layout(title_text='Distribution of Properties by Number of Bedrooms', 
                      xaxis_title='Number of Bedrooms', yaxis_title='Frequency')
    db_session.close()
    return fig.to_html(full_html=False)

def price_vs_zipcode_scatter_plot(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session)
    query = query.filter(Property.is_valid == True).filter(Property.squarefeet > 0)
    df = pd.read_sql(query.statement, db_session.bind)
    #df = pd.DataFrame(query, columns=["price", "zipcode", "squarefeet"])
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
