from enum import Enum

CONTENT_TYPE_IMAGE = ["image/jpeg", "image/png"]


class SortType(str, Enum):
    """Константы по сортировке."""

    asc = "asc"
    desc = "desc"
