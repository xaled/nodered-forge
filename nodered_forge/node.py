from typing import List, Tuple
from os.path import join

from .input import NodeParameter
from .utils import to_js_package_name, normalize_icon
from .templating import render_template, to_title


# DEFAULT_COLOR = '#a6bbcf'


class CustomAPINode:
    def __init__(self, parent, name, route, method='GET', color=None, category=None, icon=None,
                 parameters_config=None, description='No description'):
        from .app import NodeForgeApp
        self.parent: NodeForgeApp = parent
        self.name = self.parent.node_name_prefix + to_js_package_name(name)
        self.label = to_title(name)
        self.route = route
        self.method = method
        self.color = color or self.parent.default_color
        self.category = category or self.parent.default_category
        self.icon = normalize_icon(icon or self.parent.default_icon)
        # self.parameters_config = parameters_config
        self.description = description

        uri, route_params = parse_route(self.route)
        # self.url = self.parent.base_url + route
        self.url = self.parent.base_url + uri
        self.parameters = dict()
        self.parameter_list = list()

        for route_param in route_params:
            self.parameters[route_param.name] = route_param
            self.parameter_list.append(route_param.name)

        parameters_config = parameters_config or list()
        for param_init in parameters_config:
            param = NodeParameter.from_parm_init(param_init)
            if param.name in self.parameters and self.parameters[param.name].route_param:
                self.parameters[param.name].update_route_params(param)
            elif param.name not in self.parameters:
                self.parameters[param.name] = param
                self.parameter_list.append(param.name)

        for param in self.parent.global_parameters:
            if param.name not in self.parameters:
                self.parameters[param.name] = param
                self.parameter_list.append(param.name)

    def to_dict(self):
        return {
            'name': self.name,
            'route': self.route,
            'method': self.method,
            'color': self.color,
            'category': self.category,
            'icon': self.icon,
            'parameter_list': self.parameter_list,
            'parameters_config': {k: p.to_dict() for k, p in self.parameters.items()},
            'description': self.description,
            'url': self.url,
        }

    def get_defaults(self):
        params = {
            param_name: dict(
                value=self.parameters[param_name].default,
                required=self.parameters[param_name].required,
                # TODO: type & validate
            )
            for param_name in self.parameter_list
        }
        params['name'] = {"value": ""}
        return params

    def output_node_files(self, pacakge_dir):
        # js
        js_file_path = join(pacakge_dir, f"{self.name}.js")
        with open(js_file_path, 'w') as fou:
            fou.write(render_template("static/node.js", node=self))

        # html
        html_file_path = join(pacakge_dir, f"{self.name}.html")
        with open(html_file_path, 'w') as fou:
            fou.write(render_template("static/node.html", node=self))


def parse_route(route_str: str) -> Tuple[str, List[NodeParameter]]:
    route_parts = route_str.split('/')
    params = []
    parts = list()

    for route_part in route_parts:
        if route_part.startswith('<') and route_part.endswith('>'):
            route_part = route_part[1:-1]
            parameter = NodeParameter.from_str(route_part)
            parameter.required = True
            parameter.route_param = True
            params.append(parameter)
            parts.append(f"%%{parameter.name}%%")
        else:
            parts.append(route_part)

    return '/'.join(parts), params
