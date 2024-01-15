import json
import os
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Create a Jinja2 environment
jinja2_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True,  # Enable autoescaping for security
    trim_blocks=True,  # Trim leading and trailing whitespaces from blocks
    lstrip_blocks=True,  # Strip leading whitespaces from blocks
)


# Custom filters
def to_json(value):
    return json.dumps(value)


def to_title(value):
    value = value.replace('-', ' ').replace('_', ' ')
    return value[0].upper() + value[1:]


jinja2_env.filters['json'] = to_json
jinja2_env.filters['title'] = to_title


# # Example: Add global variables to the environment
# jinja2_env.globals['global_variable'] = 'This is a global variable'

def render_template(template_name, **kwargs):
    template = jinja2_env.get_template(template_name)
    return template.render(**kwargs)
