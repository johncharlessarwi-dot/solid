from pathlib import Path

from flask import Flask

from config import Config
from .extensions import csrf, db, login_manager, migrate
from .models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .admin.routes import admin_bp
    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp
    from .main.routes import main_bp
    from .orders.routes import orders_bp
    from .payments.routes import payments_bp
    from .services.routes import services_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    from .cli import register_cli

    register_cli(app)
    return app
