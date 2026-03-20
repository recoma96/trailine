from enum import StrEnum
from typing import List, Dict, Any, TypeAlias


SQLRow: TypeAlias = Dict[str, Any]
SQLRowList: TypeAlias = List[SQLRow]


class SkyCondition(StrEnum):
    SUNNY = "sunny"
    RAINY = "rainy"


class CourseLocationType(StrEnum):
    START = "start"
    MIDDLE = "middle"
    END = "end"
