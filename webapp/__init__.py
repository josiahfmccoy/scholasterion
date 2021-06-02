import os
import shutil
from contextlib import contextmanager
from datetime import datetime
from flask import Flask
from flask_api import FlaskApi
from flask_moment import Moment

api = FlaskApi()
moment = Moment()


def create_app():
    app = Flask(__name__)
    app.logger.info("Initializing new Scholasterion WebApp")

    app.secret_key = b'secret_key'

    @app.context_processor
    def inject_globals():
        return dict(
            site_name='Σχολαστήριον',
            now=datetime.utcnow()
        )

    api.init_app(app)
    init_routes(app)

    moment.init_app(app)

    def static_path(filepath):
        filepath = os.path.join(app.static_folder, filepath)
        return filepath

    app.static_path = static_path

    @contextmanager
    def open_static(filepath, *args, strict=False, **kwargs):
        filepath = app.static_path(filepath)
        if not strict and not os.path.isdir(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        with open(filepath, *args, **kwargs) as f:
            yield f

    app.open_static = open_static

    def remove_static(filepath, *args, strict=False, **kwargs):
        filepath = app.static_path(filepath)
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        elif os.path.isfile(filepath):
            os.remove(filepath)

    app.remove_static = remove_static

    from .literature.utils import load_texts
    load_texts(app)

    return app


def init_routes(app):
    from .base.routes import base
    app.register_blueprint(base)

    from .literature.api import literature_api
    app.register_blueprint(literature_api)

    from .lexemes.api import lexeme_api
    app.register_blueprint(lexeme_api)
