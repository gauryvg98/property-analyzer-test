from datetime import datetime
import pandas as pd
from db.sqlite_setup import fetch_db_session
from sqlalchemy_schemas.property import Property


def load_data(csv_file, is_filtered):
    db_session = next(fetch_db_session())
    data = pd.read_csv(csv_file)
    print("loading data...")
    print("this may take a minute...")
    properties: list[Property] = []
    for _, row in data.iterrows():
        property_entry = Property(
            propertyid=row["propertyid"],
            address=row["address"],
            city=row["city"],
            state=row["state"],
            zipcode=row["zipcode"],
            price=row["price"],
            bedrooms=row["bedrooms"],
            bathrooms=row["bathrooms"],
            squarefeet=row["squarefeet"],
            datelisted=(
                datetime.strptime(row["datelisted"], "%Y-%m-%d %H:%M:%S")
                if pd.notnull(row["datelisted"])
                else None
            ),
        )
        if property_entry.price > 0 and property_entry.squarefeet > 0:
            property_entry.price_per_square_feet = (
                property_entry.price / property_entry.squarefeet
            )

        if is_filtered and property_entry.price == 0:
            property_entry.price = None  # setting this to None to not skew our analysis

        # filter out garbage/extreme outlier data before load
        if is_filtered and check_if_extreme_outlier_during_load(
            property_entry=property_entry
        ):
            continue

        properties.append(property_entry)
        if len(properties) == 5000:
            db_session.bulk_save_objects(properties)
            db_session.commit()
            properties = []

    db_session.bulk_save_objects(properties)
    db_session.commit()
    properties = []
    db_session.close()


def check_if_extreme_outlier_during_load(property_entry) -> bool:
    price_check = False
    if property_entry.price is not None:
        price_check = property_entry.price > 500000000 or property_entry.price < 150
    ppsf_check = False
    if property_entry.price_per_square_feet is not None:
        ppsf_check = (
            property_entry.price_per_square_feet < 1
            or property_entry.price_per_square_feet > 100000
        )
    return price_check or ppsf_check
