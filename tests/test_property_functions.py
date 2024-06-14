import unittest
from unittest.mock import patch
from statistics_handlers.outlier_properties import (
    fetch_filtered_property_outliers_on_price,
    fetch_filtered_property_outliers_on_price_per_squarefeet,
)
from statistics_handlers.stats import (
    calculate_property_statistics,
)
from sqlalchemy_schemas.property import filter_properties
from pydantic_models.property import PropertyQueryParams, PageRequest, PaginatedResponse
from pydantic_models.statistics import PropertyStatisticsResponse
from mock_data import mock_session, mock_filter_property_query, df

class TestPropertyFunctions(unittest.TestCase):

    @patch('sqlalchemy_schemas.property.filter_property_query', side_effect=mock_filter_property_query)
    @patch('db.sqlite_setup.SessionLocal', return_value=mock_session)
    def test_fetch_filtered_property_outliers_on_price(self, mock_filter_query, mock_session):
        query_params = PropertyQueryParams()
        pagination = PageRequest(page=1, page_size=10)
        response = fetch_filtered_property_outliers_on_price(query_params, pagination, mock_session)
        self.assertIsInstance(response, PaginatedResponse)
        self.assertGreater(len(response.results), 0)
        # check for known outliers
        outlier_prices = [1000000, 1500000, 2000000, 2500000, 3000000]
        for result in response.results:
            self.assertIn(result['price'], outlier_prices)

    @patch('sqlalchemy_schemas.property.filter_property_query', side_effect=mock_filter_property_query)
    @patch('db.sqlite_setup.SessionLocal', return_value=mock_session)
    def test_fetch_filtered_property_outliers_on_price_per_squarefeet(self, mock_filter_query, mock_session):
        query_params = PropertyQueryParams()
        pagination = PageRequest(page=1, page_size=10)
        response = fetch_filtered_property_outliers_on_price_per_squarefeet(query_params, pagination, mock_session)
        self.assertIsInstance(response, PaginatedResponse)
        self.assertGreater(len(response.results), 0)
        # check for known outliers
        outlier_prices = [1000000, 1500000, 2000000, 2500000, 3000000]
        for result in response.results:
            self.assertIn(result['price'], outlier_prices)

    @patch('sqlalchemy_schemas.property.filter_property_query', side_effect=mock_filter_property_query)
    @patch('db.sqlite_setup.SessionLocal', return_value=mock_session)
    def test_calculate_property_statistics(self, mock_filter_query, mock_session):
        query_params = PropertyQueryParams()
        response = calculate_property_statistics(query_params, mock_session)
        self.assertIsInstance(response, PropertyStatisticsResponse)
        self.assertGreater(response.total_properties, 0)
        # check statistical values
        self.assertAlmostEqual(response.average_price, df['price'].mean())
        self.assertAlmostEqual(response.median_price, df['price'].median())
        self.assertAlmostEqual(response.average_price_per_sqft, (df['price'] / df['squarefeet']).mean())
        self.assertEqual(response.total_properties, len(df))
        # check for outlier count
        p25 = df['price'].quantile(0.25)
        p75 = df['price'].quantile(0.75)
        iqr = p75 - p25
        lower_bound = p25 - 1.5 * iqr
        upper_bound = p75 + 1.5 * iqr
        outliers_count = len(df[(df['price'] < lower_bound) | (df['price'] > upper_bound)])
        self.assertEqual(response.outlier_properties_count, outliers_count)

    @patch('sqlalchemy_schemas.property.filter_property_query', side_effect=mock_filter_property_query)
    @patch('db.sqlite_setup.SessionLocal', return_value=mock_session)
    def test_filter_properties(self, mock_filter_query, mock_session):
        query_params = PropertyQueryParams()
        pagination = PageRequest(page=1, page_size=10)
        response = filter_properties(query_params, pagination, mock_session)
        self.assertIsInstance(response, PaginatedResponse)
        self.assertGreater(len(response.results), 0)
        # check the pagination
        self.assertEqual(response.page, pagination.page)
        self.assertEqual(response.page_size, pagination.page_size)
        self.assertEqual(response.total, 100)
        self.assertEqual(len(response.results), 10)

if __name__ == '__main__':
    unittest.main()
