from flask import Flask

def create_app():
    """Inicializa a aplicação Flask e registra as rotas."""
    app = Flask(__name__)

    from .routes import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/")

    return app
