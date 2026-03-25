from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///tasks.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:5001')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=True)


with app.app_context():
    db.create_all()


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    result = []
    for t in tasks:
        task_data = {
            'id': t.id, 'title': t.title, 'description': t.description,
            'completed': t.completed, 'created_at': t.created_at.isoformat(),
            'user_id': t.user_id
        }
        # Enrich with username from auth service
        if t.user_id:
            try:
                resp = requests.get(f'{AUTH_SERVICE_URL}/api/users/{t.user_id}', timeout=2)
                if resp.status_code == 200:
                    task_data['username'] = resp.json()['username']
            except requests.exceptions.RequestException:
                task_data['username'] = None
        result.append(task_data)
    return jsonify(result)


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        user_id=data.get('user_id')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({
        'id': task.id, 'title': task.title, 'description': task.description,
        'completed': task.completed, 'created_at': task.created_at.isoformat()
    }), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({
        'id': task.id, 'title': task.title, 'description': task.description,
        'completed': task.completed
    })


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'tasks'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
