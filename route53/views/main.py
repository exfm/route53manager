from flask import redirect, Blueprint, url_for

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('zones.zones_list'))
