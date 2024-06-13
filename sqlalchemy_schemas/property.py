from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from db.sqlite_setup import Base
from sqlalchemy.orm import Session

from middleware.pagination import PageRequest
from pydantic_models.property import PaginatedResponse, PropertyQueryParams

class Property(Base):
    __tablename__ = 'properties'
    id = Column(Integer, primary_key=True, autoincrement="auto")
    propertyid = Column(Integer, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    price = Column(Float, nullable=True,)
    bedrooms = Column(Integer, nullable=True,)
    bathrooms = Column(Float, nullable=True,)
    squarefeet = Column(Float, nullable=True,)
    datelisted = Column(DateTime, nullable=True,)
    is_valid = Column(Boolean)
    is_historic = Column(Boolean)

def filter_properties(query_params:PropertyQueryParams, pagination:PageRequest, db_session:Session) -> PaginatedResponse:
    query = filter_property_query(query_params=query_params, db_session=db_session)
    count = query.count()
    query = query.offset((pagination[0]-1)*pagination[1]).limit(pagination[1])
    properties = query.all()
    db_session.close()

    return PaginatedResponse(
        page=pagination[0],
        page_size=pagination[1],
        total=count,
        results=[property.__dict__ for property in properties],
    )

def filter_property_query(query_params:PropertyQueryParams, db_session:Session):
    query = db_session.query(Property)

    # filters on price
    if query_params.price_min is not None:
        query = query.filter(Property.price >= query_params.price_min)
    if query_params.price_max is not None:
        query = query.filter(Property.price <= query_params.price_max)

    # filters on squarefeet
    if query_params.squarefeet_min is not None:
        query = query.filter(Property.squarefeet >= query_params.squarefeet_min)
    if query_params.squarefeet_max is not None:
        query = query.filter(Property.squarefeet <= query_params.squarefeet_max)

    # filters on bedrooms
    if query_params.bedrooms is not None:
        query = query.filter(Property.bedrooms == query_params.bedrooms)

    # filters on bathrooms
    if query_params.bathrooms is not None:
        query = query.filter(Property.bathrooms == query_params.bathrooms)

    # filters on zipcode
    if query_params.zipcode is not None:
        query = query.filter(Property.zipcode == query_params.zipcode)

    # filters on city
    if query_params.city is not None:
        query = query.filter(Property.city == query_params.city)

    # filters on state
    if query_params.state is not None:
        query = query.filter(Property.state == query_params.state)
    
    return query