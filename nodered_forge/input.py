import re
from dataclasses import dataclass
from enum import Enum

from .conf import TYPED_INPUT_TYPE_SUFFIX
from .type_hints import Optional, Any, Dict, List

FORBIDDEN_NAMES = ("name", "auth")

BASE_PARAM_PATTERN = r'(([a-z]+):([a-zA-Z_]+)'


class InputType(Enum):
    PLAIN = "plain"
    STR = "str"
    NUM = "num"
    BOOL = "bool"
    JSON = "json"
    DATE = "date"  # TODO timedate??
    SELECT = "select"

    # TEXT_EDITOR = "text_editor"

    @classmethod
    def get_input_type(cls, type_id: str) -> 'InputType':
        type_id = type_id.upper().strip()
        if type_id in ('STRING', 'TEXT'):
            type_id = 'STR'
        elif type_id in ('INT', 'INTEGER', 'NUMBER', 'FLOAT'):
            type_id = 'NUM'
        elif type_id == 'BOOLEAN':
            type_id = 'BOOL'

        return InputType[type_id]


@dataclass
class NodeParameter:
    name: str
    type: InputType = InputType.STR
    default: Optional[Any] = None
    required: bool = False
    plain_type: str = "text"
    route_param: bool = False
    url_param: bool = False
    options: List = None
    multiple_select: bool = False
    typed_input: bool = True

    def __post_init__(self):
        self.name = validate_parameter_name(self.name)
        self.typed_input = self.type.value not in ('plain', 'text_editor')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type.value,
            'default': self.default,
            'required': self.required,
            'plain_type': self.plain_type,
            'route_param': self.route_param,
            'url_param': self.url_param,
            'options': self.options,
            'multiple_select': self.multiple_select,
            'typed_input': self.typed_input
        }

    def update_route_params(self, other_param: 'NodeParameter'):
        self.default = self.default or other_param.default
        self.required = other_param.required
        self.plain_type = other_param.plain_type
        self.options = other_param.options

    @classmethod
    def from_dict(cls, input_dict: Dict[str, Any]) -> 'NodeParameter':
        return cls(
            name=input_dict['name'],
            type=InputType.get_input_type(input_dict['type']),
            required=input_dict['required'],
            default=input_dict.get('default', None),
            plain_type=input_dict.get('plain_type', 'text'),
            route_param=input_dict.get('route_param', False),
            url_param=input_dict.get('url_param', False),
            options=input_dict.get('options', None),
            multiple_select=input_dict.get('multiple_select', False)
        )

    @classmethod
    def from_str(cls, param_str: str) -> 'NodeParameter':
        parts = param_str.split(':')
        param_type = InputType.STR

        if len(parts) == 1:
            name = parts[0]
        else:
            name = parts[1]
            param_type = InputType.get_input_type(parts[0])

        default_value: Optional[Any] = None
        if len(parts) == 3:
            default_value = parts[2]
            if param_type == InputType.NUM:
                default_value = int(default_value)
            elif param_type == InputType.BOOL:
                default_value = not (default_value.lower().strip() == 'false')
            # elif param_type == InputType.DATE: TODO
            #     default_value = int(default_value)

        return NodeParameter(name=name, type=param_type, default=default_value)

    @classmethod
    def from_parm_init(cls, param_init: "PARAM_INIT") -> 'NodeParameter':
        if isinstance(param_init, cls):
            return param_init

        if isinstance(param_init, str):
            return cls.from_str(param_init)

        if isinstance(param_init, dict):
            return cls.from_dict(param_init)

        raise ValueError(f"Unknown param_init type {type(param_init)=}")


PARAM_INIT = str | NodeParameter | Dict[str, Any]


def validate_parameter_name(name):
    name = name.strip().lower().replace('_', '-').replace(' ', '_')

    if name.endswith(TYPED_INPUT_TYPE_SUFFIX):
        raise ValueError("Bad parameter name value: reserved for typedinput.")

    if name in FORBIDDEN_NAMES or not name[0].isalpha() or not re.match("^[a-zA-Z0-9-]+$", name):
        raise ValueError("Bad parameter name value")
    return name
