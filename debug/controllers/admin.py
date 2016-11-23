from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

admin_page = Blueprint('admin_page', __name__)
db = None


class AdminController(object):
    def __init__(self, database):
        global db
        db = database


@admin_page.route('/admin')
def index():
    return ('Display generic admin page with settings.conf settings')


@admin_page.route('/admin/<setting>', methods=['POST'])
def setting():
    # Update the <setting> in the settings.conf file to the posted value
    return redirect(url_for('admin_page.index'))


@admin_page.route('/admin/plugin', methods=['GET', 'POST', 'DELETE'])
def plugin():
    if request.method == 'POST':
        # add the posted plugin to the database
        pass
    if request.method == 'DELETE':
        # delete the posted plugin from the database
        pass
    return ('Display generic plugin info and last_run dates')
