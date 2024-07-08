from quart import Quart
from app.api.hello import hello_bp
from app.api.getMap import getMap_bp
from app.api.login import auth_bp


def create_app():
    app = Quart(__name__)
    
    app.register_blueprint(hello_bp, url_prefix='/api')
    app.register_blueprint(getMap_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    return app
    

