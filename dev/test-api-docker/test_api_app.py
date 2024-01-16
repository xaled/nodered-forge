from functools import wraps

from flask import Flask, jsonify, request

from nodered_forge import NodeForgeApp, NodeParameter, InputType

flask_app = Flask(__name__)
nodered_api = NodeForgeApp(
    "TestTodoApi", "http://test_api:5000", default_icon="fa-check-square-o", authentication=True,
    global_parameters_config=[
        NodeParameter(name="pretty", type=InputType.BOOL, default=True, url_param=True),
        # NodeParameter(name="nothing", type=InputType.STR, default="walop", url_param=True)
    ])

todos = [
    {
        'id': 1,
        'text': 'Example Todo',
        'done': False,
        'due-date': '2024-01-15',
        'tags': ['work', 'urgent'],
        'notes': 'Finish the task',
        'level': 2,
        'assigned-to': 'me'
    }
]

tags_input = NodeParameter('tags', options=['work', 'personal', 'chore', 'family'], multiple_select=True)
assigned_to_input = NodeParameter('assigned-to', options=['me', 'you', 'him', 'her'])


def require_authentication(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        flask_app.logger.info(f"{auth_header=}")
        if auth_header == 'uk6pEDvxSyUZ6bagcZGC4kMLcw8qwf2N':
            return f(*args, **kwargs)
        return {'error': 'unauthorized'}, 401

    return wrapped


@nodered_api.api_node('/todos', method='GET')
@flask_app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify({'todos': todos})


@nodered_api.api_node('/todos/<str:todo-id>', method='GET')
@flask_app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = next((item for item in todos if item['id'] == todo_id), None)
    if todo:
        return jsonify({'todo': todo})
    else:
        return jsonify({'message': 'Todo not found'}), 404


@nodered_api.api_node('/todos', method='POST', parameters_config=[
    'str:text',
    'date:due-date',
    NodeParameter('notes', type=InputType.PLAIN, plain_type='textarea'),
    'int:level',
    tags_input,
    assigned_to_input,
])
@flask_app.route('/todos', methods=['POST'])
@require_authentication
def create_todo():
    data = request.get_json()
    flask_app.logger.info(data)

    new_todo = {
        'id': len(todos) + 1,
        'text': data['text'],
        'done': data.get('done', False),
        'due-date': data.get('due-date'),
        'tags': data.get('tags', []),
        'notes': data.get('notes'),
        'level': data.get('level'),
        'assigned-to': data.get('assigned-to', 'me')
    }

    todos.append(new_todo)
    return jsonify({'todo': new_todo}), 201


@nodered_api.api_node('/todos/<int:todo_id>', method='PUT', parameters_config=[
    'str:text',
    'date:due-date',
    'bool:done',
    NodeParameter('notes', type=InputType.PLAIN, plain_type='textarea'),
    'int:level',
    tags_input,
    assigned_to_input,
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


@nodered_api.api_node('/todos/<int:todo_id>', method='DELETE')
@flask_app.route('/todos/<int:todo_id>', methods=['DELETE'])
@require_authentication
def delete_todo(todo_id):
    global todos
    todos = [item for item in todos if item['id'] != todo_id]
    return jsonify({'message': 'Todo deleted successfully'})


if __name__ == '__main__':
    nodered_api.output_package('/modules')
    # nodered_api.output_package('modules')
    flask_app.run(host="0.0.0.0", debug=True)
