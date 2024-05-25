from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for flash messages
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    color = db.Column(db.String(20))
    priority = db.Column(db.String(20))

    def __repr__(self):
        return f'<Task {self.title}>'


# Ensure database creation within the application context
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    description = request.form.get('description')  # Capture the description from the form
    # Backend validation to enforce character limits
    if len(title) > 10:
        flash('Title cannot be more than 10 characters')
        return redirect(url_for('index'))
    if description and len(description) > 20:
        flash('Description cannot be more than 20 characters')
        return redirect(url_for('index'))
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))


# New routes for updating due date, color, and priority
@app.route('/set_due_date/<int:task_id>', methods=['POST'])
def set_due_date(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    due_date = data.get('due_date')
    if due_date == 'no date':
        task.due_date = None
    elif due_date == 'today':
        task.due_date = datetime.today().date()
    elif due_date == 'tomorrow':
        task.due_date = datetime.today().date() + timedelta(days=1)
    else:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify(success=False, error="Invalid date format"), 400
    db.session.commit()
    return jsonify(success=True)


@app.route('/set_color/<int:task_id>', methods=['POST'])
def set_color(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.color = data.get('color')
    db.session.commit()
    return jsonify(success=True)


@app.route('/set_priority/<int:task_id>', methods=['POST'])
def set_priority(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.priority = data.get('priority')
    db.session.commit()
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)
