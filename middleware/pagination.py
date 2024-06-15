from fastapi import Query
from pydantic import BaseModel


class PageRequest(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(10, ge=1)


def pagination_params(
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)
) -> PageRequest:
    return PageRequest(
        page=page,
        page_size=page_size,
    )
