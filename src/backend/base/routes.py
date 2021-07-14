from flask import Blueprint, current_app, \
    send_from_directory, render_template


base = Blueprint('base', __name__)


@base.route('/', defaults={'path': ''})
@base.route('/<path:path>')
def vue_home(path):
    if path.endswith('favicon.ico'):
        current_app.logger.debug('Serving favicon')
        return send_from_directory('static/public', 'favicon.ico')

    current_app.logger.debug(f'Passing route to Vue Router: /{path}')
    return render_template('index.html')
