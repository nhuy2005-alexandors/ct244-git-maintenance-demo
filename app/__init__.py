import os

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager

from .auth import views as auth_views
from .todo import views as todo_views
from .models import UserModel


# To handle user login authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(username):
    return UserModel.query(username)


# Application factory function
def create_app() -> Flask:
    """
    Creates the Flask instance

    Return:
    app: Flask -> Flask instance
    """

    app: Flask = Flask(__name__,
                       template_folder='./templates',
                       static_folder='./static')

    bootstrap = Bootstrap5(app)
    login_manager.init_app(app)

    app.config["SECRET_KEY"] = "SUPER_SECRET_KEY"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///database.db"
    )

    # Blueprints
    app.register_blueprint(auth_views.auth)
    app.register_blueprint(todo_views.todo)

    return app
