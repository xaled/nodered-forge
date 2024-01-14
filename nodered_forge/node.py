import re
import random
from .utils import to_js_package_name
from .templating import render_template
from os.path import join

DEFAULT_COLOR = '#a6bbcf'
DEFAULT_CATEGORY = 'NodeRedForgePy'
DEFAULT_ICON = "font-awesome/fa-globe"


class CustomAPINode:
    def __init__(self, parent, name, route, method='GET', color=None, category=None, icon=None,
                 body_schema=None, description='No description'):
        from .app import NodeForgeApp
        self.parent: NodeForgeApp = parent
        self.name = to_js_package_name(name)
        self.route = route
        self.method = method
        self.color = color or DEFAULT_COLOR
        self.category = category or self.parent.name
        self.icon = icon or DEFAULT_ICON
        self.body_schema = body_schema
        self.url = self.parent.base_url + route
        self.description = description


    @staticmethod
    def parse_route(route_pattern):
        pattern = re.compile(r'<(?P<param>[^<>:]+)(?::(?P<type>[^<>]+))?>')

        # Extract route parameters and their types from the pattern
        matches = re.finditer(pattern, route_pattern)

        # Create a list of dictionaries containing parameter name and type
        route_params = [{'param': match.group('param'), 'type': match.group('type')} for match in matches]

        # Replace route parameters with placeholders for JavaScript template literals
        js_schema_route = pattern.sub('${}', route_pattern)

        # Create a schema with route and parameters
        js_schema = {
            'route': js_schema_route,
            'parameters': route_params,
        }

        return js_schema

    def output_node_files(self, pacakge_dir):
        # js
        js_file_path = join(pacakge_dir, f"{self.name}.js")
        with open(js_file_path, 'w') as fou:
            fou.write(render_template("static/node.js", node=self))

        # html
        html_file_path = join(pacakge_dir, f"{self.name}.html")
        with open(html_file_path, 'w') as fou:
            fou.write(render_template("static/node.html", node=self))


def generate_random_color(seed_string):
    # Use the hash function to generate a hash value from the input string
    hash_value = hash(seed_string)

    # Create a custom random instance for each thread
    local_random = random.Random(hash_value)

    # Generate random values for RGB components
    red = local_random.randint(0, 255)
    green = local_random.randint(0, 255)
    blue = local_random.randint(0, 255)

    # Format the RGB values into a hex color code
    color_code = "#{:02X}{:02X}{:02X}".format(red, green, blue)

    return color_code
