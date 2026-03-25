from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///todos.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


with app.app_context():
    db.create_all()


# ---- Auth routes ----
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'User already exists'}), 400
    user = User(username=data['username'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username}), 201


@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])


# ---- Task routes ----
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'id': t.id, 'title': t.title, 'description': t.description,
        'completed': t.completed, 'created_at': t.created_at.isoformat(),
        'user_id': t.user_id
    } for t in tasks])


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


# ---- Web UI ----
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
