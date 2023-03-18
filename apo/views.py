from flask import (flash, make_response, redirect, render_template,
                   request, send_file, url_for)
from flask_login import current_user, login_required, login_user, logout_user

from apo import app, db
from apo.forms import LostReportForm
from apo.models import User


'''
Routes
'''

@app.route('/', methods=['GET'])
def index():

    return render_template('home.html')


'''
SEO
'''


@app.route('/robots.txt', methods=['GET'])
def robots():

    # Return static robots.txt file for any web crawlers that use it
    return send_file('templates/seo/robots.txt')


@app.route('/favicon.ico', methods=['GET'])
def favicon():

    # Return static favicon.ico
    return send_file('static/img/apo.ico')


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():

    # Return static sitemap XML file for SEO
    sitemap_xml = render_template('seo/sitemap.xml')
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


'''
Error Handlers
'''


@app.errorhandler(404)
def page_not_found(e):

    # 404 error page
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_for_server(e):

    # 500 error page
    return render_template('500.html')