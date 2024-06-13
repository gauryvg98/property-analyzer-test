import pandas as pd
from sqlalchemy.orm import Session
from pydantic_models.property import PropertyQueryParams
from sqlalchemy_schemas.property import Property, filter_property_query
from plotly.subplots import make_subplots
import plotly.graph_objs as go

def price_distribution(query_params: PropertyQueryParams, db_session: Session):
    query = filter_property_query(query_params=query_params, db_session=db_session)
    prices = [price for price, in query]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Histogram(x=prices, nbinsx=50, marker_color='blue', opacity=0.7), row=1, col=1)
    fig.update_layout(title_text='Distribution of Property Prices', xaxis_title='Price', yaxis_title='Frequency')

    return fig.to_html(full_html=False)

def bedrooms_distribution(query_params: PropertyQueryParams, db_session: Session):
    query = db_session.query(Property.bedrooms).all()
    bedrooms = [bedroom for bedroom, in query]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Bar(x=pd.Series(bedrooms).value_counts().sort_index().index, 
                         y=pd.Series(bedrooms).value_counts().sort_index().values, 
                         marker_color='green', opacity=0.7), row=1, col=1)
    fig.update_layout(title_text='Distribution of Properties by Number of Bedrooms', 
                      xaxis_title='Number of Bedrooms', yaxis_title='Frequency')

    return fig.to_html(full_html=False)