from flask import Flask

from app.views.public import public_bp
from app.views.admin import admin_bp
from app.views.auth import auth_bp
import yaml
from .models.app_models import db, User
from flask_login import LoginManager


def create_app():
    app = Flask(__name__)
    with open('app/config/config.yml', 'r') as f:
        config = yaml.safe_load(f)
    app.config.update(config["development"])
    db.init_app(app)
    with app.app_context():
        db.create_all()
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_redirect'

    @login_manager.user_loader
    def load_user(user_id):
        # Flask-Login requires this function to load a user
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(public_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.template_folder = "../templates"
    app.static_folder = "../static"
    return app