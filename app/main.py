from quart import Quart
from quart_jwt_extended import JWTManager
from .Config import Config
from app.api.Normal import Normal_bp
from app.api.login import auth_bp
from app.api.protect import protect_bp


def create_app():
    app = Quart(__name__)
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY  # 在生产环境中应使用复杂的密钥

    jwt = JWTManager(app)
    app.register_blueprint(Normal_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(protect_bp, url_prefix='/api')
    return app
    

