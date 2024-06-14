import pandas as pd

def sanitize_pandas_dataframe(df:pd.DataFrame)-> list:
    outlier_records = df.to_dict(orient='records')
    sanitized_records = []
    for record in outlier_records:
        sanitized_record = {}
        for key, value in record.items():
            if pd.isna(value):
                sanitized_record[key] = None
            else:
                sanitized_record[key] = value
        sanitized_records.append(sanitized_record)
    return sanitized_records

def calculate_outliers(df: pd.DataFrame, series: pd.Series) -> pd.DataFrame:
    p25 = series.quantile(0.25)
    p75 = series.quantile(0.75)
    
    iqr = p75-p25

    lower_bound = p25 - (1.5*iqr)
    upper_bound = p75 + (1.5*iqr)

    outliers = df[(series < lower_bound) | (series > upper_bound)]
    return outliers

def forwardfill_price_for_historical_property_data(df: pd.DataFrame) -> pd.DataFrame:
    df['datelisted'] = pd.to_datetime(df['datelisted']).dt.to_period('M')
    
    all_periods = pd.period_range(start=df['datelisted'].min(), end=df['datelisted'].max(), freq='M')
    all_propertyids = df['propertyid'].unique()
    complete_index = pd.MultiIndex.from_product([all_propertyids, all_periods], names=['propertyid', 'datelisted'])
    df.set_index(['propertyid', 'datelisted'], inplace=True)
    df = df.reset_index().drop_duplicates(subset=['propertyid', 'datelisted']).set_index(['propertyid', 'datelisted'])
    df = df.reindex(complete_index).sort_index()
    df = df.groupby('propertyid').ffill().reset_index()

    return df

def sqlalchemy_models_to_dataframe(models):
    """
    Convert a list of SQLAlchemy model instances to a pandas DataFrame.
    
    Args:
    models (list): List of SQLAlchemy model instances.
    
    Returns:
    pd.DataFrame: DataFrame containing the data from the SQLAlchemy models.
    """
    if not models:
        return pd.DataFrame()

    # Extract the column names from the first model instance
    columns = models[0].__table__.columns.keys()
    
    # Extract data from each model instance
    data = []
    for model in models:
        row = {column: getattr(model, column) for column in columns}
        data.append(row)
    
    # Create DataFrame from the list of dictionaries
    df = pd.DataFrame(data, columns=columns)
    
    return df