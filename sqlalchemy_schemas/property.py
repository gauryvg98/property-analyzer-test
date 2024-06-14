from sqlalchemy import Column, Index, Integer, String, Float, DateTime, and_, func
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
    price_per_square_feet = Column(Float,nullable=True)
    datelisted = Column(DateTime, nullable=True,)

    __table_args__ = (
        Index('ix_property_propertyid_datelisted', 'propertyid', 'datelisted'),
    )

def filter_properties(query_params:PropertyQueryParams, pagination:PageRequest, db_session:Session) -> PaginatedResponse:
    query = filter_property_query(query_params=query_params, db_session=db_session)
    count = query.count()
    query = query.offset((pagination.page-1)*pagination.page_size).limit(pagination.page_size)
    properties = query.all()
    db_session.close()

    return PaginatedResponse(
        page=pagination.page,
        page_size=pagination.page_size,
        total=count,
        results=[property.__dict__ for property in properties],
    )

def filter_property_query(query_params:PropertyQueryParams, db_session:Session, columns: list = [], existing_query=None, latest:bool = True):
    query = existing_query
    if existing_query is None:
        if len(columns) == 0:
            query = db_session.query(Property)
        else:
            query = db_session.query(*columns)
    if query_params == None:
        return query
    # filters on price
    if query_params.price_min is not None:
        query = query.filter(Property.price >= query_params.price_min)
    if query_params.price_max is not None:
        query = query.filter(Property.price <= query_params.price_max)
    
    # filters on price per square feet
    if query_params.price_per_square_feet_min is not None:
        query = query.filter(Property.price_per_square_feet >= query_params.price_per_square_feet_min)
    if query_params.price_per_square_feet_max is not None:
        query = query.filter(Property.price_per_square_feet <= query_params.price_per_square_feet_max)

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
    
    # latest = false for historic data -> it would fetch all datelist prices in the table
    if latest:
        subquery = db_session.query(
            Property.propertyid,
            func.max(Property.datelisted).label('max_datelisted')
        ).filter(Property.datelisted != None).group_by(Property.propertyid).subquery()

        query = query.outerjoin(
            subquery,
            and_(
                Property.propertyid == subquery.c.propertyid,
                Property.datelisted == subquery.c.max_datelisted
            )
        ).filter(
            (Property.datelisted == subquery.c.max_datelisted) | (Property.datelisted == None)
        )

    return query
