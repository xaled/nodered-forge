from flask import Flask, jsonify, request
from nodered_forge import NodeForgeApp

flask_app = Flask(__name__)
nodered_api = NodeForgeApp("TestTodoApi", "http://test_api:5000")

todos = [
    {
        'id': 1,
        'text': 'Example Todo',
        'done': False,
        'due_date': '2024-01-15',
        'tags': ['work', 'urgent'],
        'notes': 'Finish the task',
        'level': 2,
        'assigned_to': 'me'
    }
]


@nodered_api.api_node('/todos', method='GET')
@flask_app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify({'todos': todos})


@nodered_api.api_node('/todos/<int:todo_id>', method='GET')
@flask_app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = next((item for item in todos if item['id'] == todo_id), None)
    if todo:
        return jsonify({'todo': todo})
    else:
        return jsonify({'message': 'Todo not found'}), 404


@nodered_api.api_node('/todos', method='POST', body_schema=[
    'str:text',
    'date:due_date',
    'text_editor:notes',
    'int:level',
    # TODO
    # ':tags',
    # ':assigned_to',
])
@flask_app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()

    new_todo = {
        'id': len(todos) + 1,
        'text': data['text'],
        'done': data.get('done', False),
        'due_date': data.get('due_date'),
        'tags': data.get('tags', []),
        'notes': data.get('notes'),
        'level': data.get('level'),
        'assigned_to': data.get('assigned_to', 'me')
    }

    todos.append(new_todo)
    return jsonify({'todo': new_todo}), 201


@nodered_api.api_node('/todos/<int:todo_id>', method='PUT', body_schema=[
    'str:text',
    'date:due_date',
    'text_editor:notes',
    'int:level',
    # TODO
    # ':tags',
    # ':assigned_to',
])
@flask_app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = next((item for item in todos if item['id'] == todo_id), None)
    if todo:
        data = request.get_json()

        todo.update({
            'text': data.get('text', todo['text']),
            'done': data.get('done', todo['done']),
            'due_date': data.get('due_date', todo['due_date']),
            'tags': data.get('tags', todo['tags']),
            'notes': data.get('notes', todo['notes']),
            'level': data.get('level', todo['level']),
            'assigned_to': data.get('assigned_to', todo['assigned_to'])
        })

        return jsonify({'todo': todo})
    else:
        return jsonify({'message': 'Todo not found'}), 404


@nodered_api.api_node('/todos/<int:todo_id>', method='DELETE')
@flask_app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [item for item in todos if item['id'] != todo_id]
    return jsonify({'message': 'Todo deleted successfully'})


if __name__ == '__main__':
    nodered_api.output_package('/modules')
    flask_app.run(host="0.0.0.0", debug=True)
