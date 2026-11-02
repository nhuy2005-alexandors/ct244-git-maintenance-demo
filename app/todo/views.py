from webbrowser import get
from flask import (Blueprint, flash, redirect, render_template,
                   url_for)
from flask_login import login_user, current_user
from app.forms import CreateToDoForm, DeleteToDoForm
from app.models import db, User, UserModel, get_todo, get_user, ToDo

todo = Blueprint('todo', __name__, url_prefix='/todo')


@todo.route('/create', methods=['POST'])
def create_todo():

    create_todo_form = CreateToDoForm()

    if create_todo_form.validate_on_submit():
        user = current_user.id
        print(user)
        user_db = get_user(user)
        print(user_db)
        description = create_todo_form.description.data

        new_todo = ToDo(description=description, id_user=user_db.id)

        db.session.add(new_todo)
        db.session.commit()

        flash('To Do created successfully!', 'success')

        return redirect(url_for('index'))


@todo.route('/done/<todo_id>', methods=['POST'])
def done_todo(todo_id):

    user = current_user.id
    user_db = get_user(user)
    user_id = user_db.id

    done_todo = get_todo(id_user=user_id, id=todo_id)

    done_todo.done = True

    db.session.commit()

    flash('To Do done successfully!', 'success')

    return redirect(url_for('index'))


@todo.route('/delete/<todo_id>', methods=['POST'])
def delete_todo(todo_id):

    user = current_user.id
    user_db = get_user(user)
    user_id = user_db.id

    delete_todo = get_todo(id_user=user_id, id=todo_id)

    db.session.delete(delete_todo)
    db.session.commit()

    flash('To Do deleted successfully!', 'success')

    return redirect(url_for('index'))
