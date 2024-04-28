import math
from datetime import datetime

from pydantic import BaseModel

from app.consts import SortType


class ObjSchema(BaseModel):
    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ")}
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        use_enum_values = True
        validate_assignment = True
        orm_mode = True


class PaginationSchema(ObjSchema):
    """Схема запроса с пагинацией"""

    page: int = 1
    page_size: int | None = None
    sort_by: str | None = None
    sort_type: SortType | None = SortType.asc


class PaginatedResponse(ObjSchema):
    count: int | None
    page_size: int | None
    pages: int | None

    @classmethod
    def get_pages(cls, count: int | None, page_size: int | None):
        if page_size is not None:
            pages = math.ceil(count / page_size) if count and page_size != 0 else 0
        else:
            page_size, pages = count, 1

        return pages, page_size
