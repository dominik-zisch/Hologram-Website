import os
from flask import Blueprint, current_app, render_template, jsonify, request

main = Blueprint('main', __name__)

@main.route('/select', methods=['GET', 'POST'])
def select_image():
    image_folder = current_app.config['IMAGE_FOLDER']
    images = [f for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]

    if request.method == 'POST':
        selected = request.form.get('image')
        if selected:
            current_app.config['SELECTED_IMAGE']['filename'] = selected
    selected = current_app.config['SELECTED_IMAGE']['filename']
    return render_template('select.html', images=images, selected=selected)

@main.route('/display')
def display():
    return render_template('display.html')

@main.route('/current_image')
def current_image():
    filename = current_app.config['SELECTED_IMAGE']['filename']
    if filename:
        return jsonify({"filename": f"/static/images/{filename}"})
    else:
        return jsonify({"filename": None})
