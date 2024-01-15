import shutil
from typing import List
from os.path import join, abspath, exists
from os import makedirs
import json

from .node import CustomAPINode
from .utils import to_js_package_name, generate_bright_color

DEFAULT_ICON = "font-awesome/fa-globe"


class NodeForgeApp:
    def __init__(self, name, base_url, ignore_ssl_errors=False, auth_type=None,
                 package_name=None,
                 default_icon=None, default_color=None, default_category=None):
        self.name = name
        self.base_url = base_url
        self.ignore_ssl_errors = ignore_ssl_errors
        self.auth_type = auth_type
        self.default_category = default_category or name
        self.default_icon = default_icon or DEFAULT_ICON
        self.default_color = default_color or generate_bright_color(self.name)
        self.api_nodes: List[CustomAPINode] = list()
        self.package_name = package_name or f"node-red-contrib-nodered-forge-{to_js_package_name(name)}"
        self.node_name_prefix = f"{to_js_package_name(name)}-"

    def register_api_node(self, name, route, method='GET', parameters_config=None, **kwargs):
        self.api_nodes.append(
            CustomAPINode(self, name, route, method=method, parameters_config=parameters_config, **kwargs))

    def api_node(self, route, name=None, method='GET', parameters_config=None, **kwargs):
        def decorator(func):
            self.register_api_node(name or func.__name__, route, method=method, parameters_config=parameters_config,
                                   **kwargs)
            return func

        return decorator

    def output_package(self, output_dir):
        output_dir = abspath(output_dir)
        pacakge_dir = join(output_dir, self.package_name)
        if exists(pacakge_dir):
            shutil.rmtree(pacakge_dir)

        makedirs(pacakge_dir)

        # package.json
        package_json_path = join(pacakge_dir, 'package.json')
        with open(package_json_path, 'w') as fou:
            json.dump({
                "name": self.package_name,
                "node-red": dict(nodes={node.name: f"{node.name}.js" for node in self.api_nodes})
            }, fou, indent=3)

        # nodes files
        for node in self.api_nodes:
            node.output_node_files(pacakge_dir)
