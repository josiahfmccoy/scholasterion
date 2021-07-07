from flask import Blueprint, render_template


base = Blueprint('base', __name__)


@base.route('/', defaults={'path': ''})
@base.route('/<path:path>')
def index(path):
    return render_template('base/index.html')
