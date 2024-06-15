import unittest
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from statistics_handlers.outlier_properties import (
    fetch_filtered_property_outliers_on_price,
    fetch_filtered_property_outliers_on_price_per_squarefeet,
)
from statistics_handlers.stats import (
    calculate_property_statistics,
)
from sqlalchemy_schemas.property import Property, filter_properties, Base  # Import the Property class and Base
from pydantic_models.property import PageRequest, PaginatedResponse
from pydantic_models.statistics import PropertyStatisticsResponse

# Setup for the in-memory SQLite database
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

# Insert mock data into the session
session = Session()

data = [
        Property(propertyid=i, price=50000 + i * 1000, squarefeet=500 + i * 10, price_per_square_feet=(50000 + i * 1000) / (500 + i * 10), zipcode = '', state = '', city = '', address = '')
            for i in range(95)
    ] + [
    Property(propertyid=i, price=price, squarefeet=squarefeet, price_per_square_feet=1000, zipcode = '', state = '', city = '', address = '')
            for i, (price, squarefeet) in enumerate(zip([1000000, 1500000, 2000000, 2500000, 3000000], [1000, 1500, 2000, 2500, 3000]), start=95)
    ]

session.add_all(data)
session.commit()

class TestPropertyFunctions(unittest.TestCase):

    def setUp(self):
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_filter_properties(self):
        #query_params = PropertyQueryParams()
        pagination = PageRequest(page=1, page_size=10)
        response = filter_properties(query_params=None, pagination=pagination, db_session=self.session)
        self.assertIsInstance(response, PaginatedResponse)
        # check the pagination
        self.assertEqual(response.page, pagination.page)
        self.assertEqual(response.page_size, pagination.page_size)
        self.assertEqual(response.total, 100)
        self.assertEqual(len(response.results), 10)

    def test_fetch_filtered_property_outliers_on_price(self):
        #query_params = PropertyQueryParams()
        pagination = PageRequest(page=1, page_size=10)
        response = fetch_filtered_property_outliers_on_price(query_params=None, pagination=pagination, db_session=self.session)
        self.assertIsInstance(response, PaginatedResponse)
        self.assertGreater(len(response.results), 0)
        # check for known outliers
        outlier_prices = [1000000, 1500000, 2000000, 2500000, 3000000]
        for result in response.results:
            self.assertIn(result.price, outlier_prices)

    def test_fetch_filtered_property_outliers_on_price_per_squarefeet(self):
        #query_params = PropertyQueryParams()
        pagination = PageRequest(page=1, page_size=10)
        response = fetch_filtered_property_outliers_on_price_per_squarefeet(query_params=None, pagination=pagination, db_session=self.session)
        self.assertIsInstance(response, PaginatedResponse)
        self.assertGreater(len(response.results), 0)
        # check for known outliers
        outlier_prices = [1000000, 1500000, 2000000, 2500000, 3000000]
        for result in response.results:
            self.assertIn(result.price, outlier_prices)

    def test_calculate_property_statistics(self):
        response = calculate_property_statistics(query_params=None, db_session=self.session)
        self.assertIsInstance(response, PropertyStatisticsResponse)
        self.assertGreater(response.total_properties, 0)
        # check statistical values
        prices = [prop.price for prop in self.session.query(Property).all()]
        p50 = pd.Series(prices).quantile(0.50)
        p25 = pd.Series(prices).quantile(0.25)
        p75 = pd.Series(prices).quantile(0.75)
        self.assertAlmostEqual(response.average_price, self.session.query(func.avg(Property.price)).scalar())
        self.assertAlmostEqual(response.median_price, p50)
        self.assertAlmostEqual(response.average_price_per_sqft, self.session.query(func.avg(Property.price / Property.squarefeet)).scalar())
        self.assertEqual(response.total_properties, self.session.query(Property).count())
        # check for outlier count
        iqr = p75 - p25
        lower_bound = p25 - 1.5 * iqr
        upper_bound = p75 + 1.5 * iqr
        outliers_count = len([price for price in prices if price < lower_bound or price > upper_bound])
        self.assertEqual(response.outlier_properties_count, outliers_count)

if __name__ == '__main__':
    unittest.main()
