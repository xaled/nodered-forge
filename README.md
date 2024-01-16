# NodeRedForgePy
NodeRedForgePy is a Python-based tool designed to facilitate the generation of custom JSON API nodes for Node-RED.

![NodeRedForgePy Screenshot](/doc/images/example.png)
<!-- ![NodeRedForgePy Screenshot 2](/doc/images/example2.png) -->

## Installation
To install NodeRedForgePy, use the following pip command:

```bash
pip install nodered-forge
```

## Usage
### NodeForgeApp
To create custom API nodes for Node-RED, start by defining the application name and the base URL:

```python
from nodered_forge import NodeForgeApp

nodeforge_app = NodeForgeApp("TestTodoApi", "http://test_api:5000")
```

Additional options for initializing `NodeForgeApp` include:

```python
NodeForgeApp(name, base_url,
    ignore_ssl_errors=False,
    authentication=False, # Whether authentication is required for API requests.
    authentication_header='Authorization', # Header used for authentication
    package_name=None, # package name for generated Node-RED module
    default_icon=None,
    default_color=None, # HTML Color, a default color is generated randomly
    default_category=None,
    global_parameters_config=None # Global configuration for parameters shared across all API nodes
    ):
```

### Creating API nodes
API nodes can be created using either the method `nodeforge_app.register_api_node()` or the decorator `@nodeforge_app.api_node()`.

Example:

```python
@nodeforge_app.api_node('/todos/<str:todo_id>', method='GET')
@flask_app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = next((item for item in todos if item['id'] == todo_id), None)
    if todo:
        return jsonify({'todo': todo})
    else:
        return jsonify({'message': 'Todo not found'}), 404
```

Other options for adding API nodes include:
```python
nodeforge_app.register_api_node(
    name, # for api_node decorator the name can be taken from the function name
    route,
    method='GET',
    color=None, # HTML color code
    category=None, # Category in Node-red pallet
    icon=None,
    parameters_config=None,  # Configuration for API parameters
    description='No API description is provided'
    ):
```

### API Parameters
API parameters can be set in three ways:

1. Using the `route` argument of either the method `nodeforge_app.register_api_node()` or the decorator `@nodeforge_app.api_node()`.
2. Using the `parameters_config` argument of either the method `nodeforge_app.register_api_node()` or the decorator `@nodeforge_app.api_node()`. This parameter accepts a list of parameter strings, dictionaries, or instances of `NodeParameter`.
3. Using the `global_parameters` argument in the initialization of `NodeForgeApp`. This argument accepts the same formats as `parameters_config`.

#### Parameter Strings

Parameter strings accept the following formats:

- `param_name`
- `param_type:param_name`
- `param_type:param_name:default_value`

### NodeParameter

There are three types of API parameters:
- Route parameters (constructing the URI stem),
- URL parameters (sent as URL-encoded key-values),
- Body parameters (sent as JSON).

Initialization options for `NodeParameter`:
```python
NodeParameter(
    name,
    type=InputType.STR,
    default=None, # Default value
    required=False
    plain_type="text" # For plain input type, specifies the HTML input type.
    route_param=False
    url_param=False
    options=None # List of options for parameters with a predefined set of values,
                 # Accepts an iterator either strings, value & label tuples,or dictionaries with value and label keys
    multiple_select=False # Allows selecting multiple values if options are defined
    ):
```

### InputType

Input types accepted by `NodeParameter`:

- InputType.PLAIN
- InputType.STR
- InputType.NUM
- InputType.BOOL
- InputType.JSON
- InputType.DATE
- InputType.SELECT

All these types correspond to Node-RED [TypedInput Widget](https://nodered.org/docs/api/ui/typedInput/#options-types) types,
except for `InputType.PLAIN`, which uses a plain HTML input (you can set the type of the input using the `plain_type` argument).

Example:
```python
@nodeforge_app.api_node('/todos/<int:todo_id>', method='PUT', parameters_config=[
    'str:text',
    'date:due-date',
    'bool:done',
    NodeParameter('notes', type=InputType.PLAIN, plain_type='textarea'),
    'int:level',
    NodeParameter('tags', options=['work', 'personal', 'chore', 'family'], multiple_select=True),
    NodeParameter('assigned-to', options=['me', 'you', 'him', 'her']),
    NodeParameter(name="pretty", type=InputType.BOOL, default=True, url_param=True),
])
@flask_app.route('/todos/<int:todo_id>', methods=['PUT'])
@require_authentication
def update_todo(todo_id):
    todo = next((item for item in todos if item['id'] == todo_id), None)
    if todo:
        data = request.get_json()

        todo.update({
            'text': data.get('text', todo['text']),
            'done': data.get('done', todo['done']),
            'due-date': data.get('due-date', todo['due-date']),
            'tags': data.get('tags', todo['tags']),
            'notes': data.get('notes', todo['notes']),
            'level': data.get('level', todo['level']),
            'assigned-to': data.get('assigned-to', todo['assigned-to'])
        })

        return jsonify({'todo': todo})
    else:
        return jsonify({'message': 'Todo not found'}), 404
```

## JSON Body Request
If a body parameter (neither `route_param` nor `url_param` is set to True) is included in the node config, a JSON body property is added to the custom node.
If this field is filled, body parameters from the form will be ignored, giving the user a way to send custom objects.

![JSON Body Request Screenshot](/doc/images/json_body.png)

### Generating Custom Nodes
After configuring the nodes, you can generate them using the `output_package` method:

```python
nodeforge_app.output_package('/modules')
```

This will create a package directory under `/modules` with the prefix "node-red-contrib-nodered-forge-" unless the `package_name` is specified in the initialization of `NodeForgeApp`.

To install the generated module in Node-RED, run the following commands:

```bash
cd /path/to/node-red/data/
npm install /modules/package-name
```

Restart Node-RED if the module is installed or updated.

## Test App
An example app can be found under `dev/test-api-docker/test_api_app.py`, which is a dummy todo manager with CRUD operations. There is also a Docker Compose file with both this app and Node-RED to test the app; don't forget to restart upon making changes to the test app.