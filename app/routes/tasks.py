from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Task, User
from ..extensions import db
from ..schemas import TaskSchema

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    query = Task.query.filter_by(user_id=int(user_id))
    completed = request.args.get('completed')
    if completed is not None:
        query = query.filter_by(completed=completed.lower() == 'true')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'tasks': tasks_schema.dump(paginated.items),
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page
    })

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=int(user_id)).first()
    if not task:
        return jsonify({'msg': 'Task not found'}), 404
    return jsonify(task_schema.dump(task))

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    # Validate input using Marshmallow
    try:
        valid_data = task_schema.load(data)
    except Exception as e:
        return jsonify({'msg': 'Invalid input', 'error': str(e)}), 400
    task = Task(
        title=valid_data['title'],
        description=valid_data.get('description', ''),
        user_id=int(user_id)
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task_schema.dump(task)), 201

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=int(user_id)).first()
    if not task:
        return jsonify({'msg': 'Task not found'}), 404
    data = request.get_json()
    # Validate input using Marshmallow (partial=True for PATCH-like behavior)
    try:
        valid_data = task_schema.load(data, partial=True)
    except Exception as e:
        return jsonify({'msg': 'Invalid input', 'error': str(e)}), 400
    if 'title' in valid_data:
        task.title = valid_data['title']
    if 'description' in valid_data:
        task.description = valid_data['description']
    if 'completed' in valid_data:
        task.completed = valid_data['completed']
    db.session.commit()
    return jsonify(task_schema.dump(task))

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=int(user_id)).first()
    if not task:
        return jsonify({'msg': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'msg': 'Task deleted'})

@tasks_bp.route('', methods=['OPTIONS'])
def options_tasks():
    return '', 200

@tasks_bp.route('/<int:task_id>', methods=['OPTIONS'])
def options_task(task_id):
    return '', 200
