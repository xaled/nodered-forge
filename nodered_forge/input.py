import re
from dataclasses import dataclass
from enum import Enum

from .conf import TYPED_INPUT_TYPE_SUFFIX
from .type_hints import Optional, Any, Dict, List

FORBIDDEN_NAMES = ("name", "authentication", 'id', 'type', 'wires', 'inputs', 'outputs', 'json_body')
ALLOWED_PLAIN_INPUT_TYPES = ("text", "password", "checkbox", "radio", "color", "date", "datetime-local", "email",
                             "month", "number", "tel", "time", "url", "week", "textarea")

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
        elif type_id in ('TIMESTAMP', 'TIME', 'DATETIME'):
            type_id = 'DATE'

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
    param_group: str = None

    def __post_init__(self):
        self.name = validate_parameter_name(self.name)
        self.typed_input = self.type.value not in ('plain', 'text_editor')
        self.plain_type = self.plain_type.strip().lower()
        if self.plain_type not in ALLOWED_PLAIN_INPUT_TYPES:
            raise ValueError(f"Unsupported plain input type: {self.plain_type}")

        self.options = [_process_option(option) for option in self.options] if self.options else None
        if self.url_param:
            self.param_group = 'URL Parameters'
        elif self.route_param:
            self.param_group = 'Route Parameters'
        else:
            self.param_group = 'Body Parameters'

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
            'typed_input': self.typed_input,
            'param_group': self.param_group
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
    def from_str(cls, param_str: str, **kwargs) -> 'NodeParameter':
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

        return NodeParameter(name=name, type=param_type, default=default_value, **kwargs)

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
    name = name.strip().lower().replace(' ', '_')

    if len(name) == 1 or name in FORBIDDEN_NAMES:
        raise ValueError(f"Bad parameter name {name=}: "
                         "reserved names (https://nodered.org/docs/creating-nodes/properties#reserved-property-names).")

    if name.endswith(TYPED_INPUT_TYPE_SUFFIX):
        raise ValueError(f"Bad parameter name {name=}: reserved for typedinput.")

    if not name[0].isalpha() or not re.match("^[a-zA-Z0-9-_]+$", name):
        raise ValueError(f"Bad parameter name {name=}:"
                         f" only letters, numbers, hyphens and underscores in a string are allowed.")
    return name


def _process_option(option):
    if isinstance(option, str):
        value, label = option, option
    elif isinstance(option, (tuple, list)) and len(option) == 2:
        value, label = option[0], option[1]
    elif isinstance(option, dict):
        value, label = option['value'], option['label']
    else:
        raise ValueError(f"Bad Option {option=}: options should be an iterator either strings, value & label tuples,"
                         " or dictionaries with value and label keys!")

    value = value.strip().lower().replace(' ', '_')

    if not value[0].isalpha() or not re.match("^[a-zA-Z0-9-]+$", value):
        raise ValueError(f"Bad Option value {value=}: "
                         f"only letters, numbers, hyphens and underscores in a string are allowed.")

    return dict(value=value, label=label)
