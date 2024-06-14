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
    print(outliers)
    return outliers