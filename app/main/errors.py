# -*- coding:utf-8 -*-
from . import main
from flask import render_template, request, jsonify

# 对于只接受json格式不接受html格式的客户端只提供json响应
@main.app_errorhandler(404)
def page_not_found(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404

@main.app_errorhandler(403)
def forbidden_enter(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403


@main.app_errorhandler(500)
def forbidden_enter(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'server internal error'})
        response.status_code = 500
        return response
    return render_template('403.html'), 500