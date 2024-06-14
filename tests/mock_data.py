import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
from sqlalchemy_schemas.property import Property

# Create a SQLite in-memory database for testing
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()
# Create the table based on your Property class schema
Property.__table__.create(bind=engine)

# Create a mock dataframe with known outliers
data = {
    'id': range(1, 101),
    'propertyid': range(1, 101),
    'address': [''] * 100,
    'city': [''] * 100,
    'state': [''] * 100,
    'zipcode': [''] * 100,
    'price': [50000 + i * 1000 for i in range(95)] + [1000000, 1500000, 2000000, 2500000, 3000000],
    'bedrooms': [1] * 100,
    'bathrooms': [1.0] * 100,
    'squarefeet': [500 + i * 10 for i in range(95)] + [1000, 1500, 2000, 2500, 3000],
    'price_per_square_feet': [(50000 + i * 1000) / (500 + i * 10) for i in range(95)] + [1000, 1000, 1000, 1000, 1000],
    'datelisted': [None] * 100,
}

df = pd.DataFrame(data)

# Use pandas to_sql to create a temporary table in SQLite
df.to_sql('properties', engine, index=False, if_exists='replace')

# Mock the database session
def mock_filter_property_query(query_params, db_session):
    return db_session.query(Property)

mock_session = MagicMock(spec=Session)
mock_session.query = MagicMock()
mock_session.query().all.return_value = session.query(Property).all()
