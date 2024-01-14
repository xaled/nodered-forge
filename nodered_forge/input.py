from type_hints import Optional, Any
from dataclasses import dataclass
from enum import Enum


@dataclass
class ParamInput:
    name: str
    type: str = "str"
    default: Optional[Any] = None
    plain_type: str = "text"


class InputType(Enum):
    PLAIN = "plain"
    STR = "str"
    NUM = "num"
    BOOL = "bool"
    JSON = "json"
    DATE = "date"
    SELECT = "select"
    TEXT_EDITOR = "text_editor"
