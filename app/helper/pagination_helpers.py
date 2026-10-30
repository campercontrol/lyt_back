from typing import Optional

from fastapi import Query
from sqlalchemy import String, Text, asc, desc, func

from schema.pagination.pagination_schema import SortEnum, Pagination,PaginationOut

def pagination_params(
    page: int = Query(ge=1, required=False, default=1, le=500000),
    per_page: int = Query(ge=1, required=False, default=10, le=100),
    order: SortEnum = SortEnum.DESC,
    sort_field: Optional[str] = None
):
    offset = page - 1 if page == 1 else (page - 1) * per_page    
    return PaginationOut(perPage=per_page, page=page, order=order.value, offset=offset, sort_field=sort_field)

def get_number_of_pages(pages_count: int, per_page: int) -> int:
    rest = pages_count % per_page
    quotient = pages_count // per_page
    return quotient if not rest else quotient + 1

def build_order_by(pagination, sort_map: dict, default: list, tiebreak=None) -> list:
    """Orden por la columna pedida en sort_field (solo si esta en sort_map); si no, el orden por defecto.

    Los textos se comparan sin distinguir mayusculas y los nulos van al final.
    """
    expr = sort_map.get(pagination.sort_field) if pagination.sort_field else None
    if expr is None:
        return default
    if isinstance(expr.type, (String, Text)):
        expr = func.lower(expr)
    direction = desc if pagination.order == SortEnum.DESC else asc
    clauses = [direction(expr).nulls_last()]
    if tiebreak is not None:
        clauses.append(tiebreak)
    return clauses
