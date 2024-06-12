from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from db.sqlite_setup import Base

class Property(Base):
    __tablename__ = 'properties'
    id = Column(Integer, primary_key=True, autoincrement="auto")
    propertyid = Column(Integer, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    price = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    squarefeet = Column(Float)
    datelisted = Column(DateTime, nullable=True,)
    is_valid = Column(Boolean)
    is_historic = Column(Boolean)