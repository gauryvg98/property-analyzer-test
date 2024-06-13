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