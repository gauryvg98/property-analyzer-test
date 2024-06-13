from datetime import datetime
import pandas as pd
from db.sqlite_setup import fetch_db_session
from sqlalchemy_schemas.property import Property

def load_data(csv_file):
    db_session = next(fetch_db_session())
    data = pd.read_csv(csv_file)
    print("loading data...")
    print("this may take a minute...")
    properties:list[Property] = []
    for _, row in data.iterrows():
        property_entry = Property(
            propertyid=row['propertyid'],
            address=row['address'],
            city=row['city'],
            state=row['state'],
            zipcode=row['zipcode'],
            price=row['price'],
            bedrooms=row['bedrooms'],
            bathrooms=row['bathrooms'],
            squarefeet=row['squarefeet'],
            datelisted=datetime.strptime(row['datelisted'], '%Y-%m-%d %H:%M:%S') if pd.notnull(row['datelisted']) else None,           
        )
        if property_entry.price == 0:
            property_entry.price = None

        if property_entry.price == None:
            property_entry.is_valid = False
            #property_entry.is_historic = False
        else:
            property_entry.is_valid = True
            #property_entry.is_historic = True
        properties.append(property_entry)

    db_session.bulk_save_objects(properties)
    db_session.commit()
    db_session.close()
