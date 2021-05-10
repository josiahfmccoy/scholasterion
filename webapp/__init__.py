import os
import shutil
from contextlib import contextmanager
from datetime import datetime
from flask import Flask
from flask_api import FlaskApi
from flask_moment import Moment
from lxml import etree

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

    load_texts(app)

    return app


def init_routes(app):
    from .base.routes import base
    app.register_blueprint(base)

    from .base.api import base_api
    app.register_blueprint(base_api)


def load_texts(app):
    text_folder = os.getenv('TEXTS_FOLDER')

    app.remove_static('data')

    parser = etree.XMLParser(remove_blank_text=True)
    for fname in os.listdir(text_folder):
        if not fname.endswith('.xml'):
            continue
        txt = etree.parse(os.path.join(text_folder, fname), parser)
        with app.open_static(f'data/{fname}', 'wb') as f:
            f.write(etree.tostring(txt, encoding='utf-8', pretty_print=True))
