import os
from flask import Blueprint, current_app, render_template, jsonify, request

main = Blueprint('main', __name__)

IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
VIDEO_EXTENSIONS = ('mp4', 'webm', 'mov')

@main.route('/select', methods=['GET', 'POST'])
def select_media():
    media_folder = current_app.config['IMAGE_FOLDER']
    all_files = os.listdir(media_folder)

    images = [f for f in all_files if f.lower().endswith(IMAGE_EXTENSIONS)]
    videos = [f for f in all_files if f.lower().endswith(VIDEO_EXTENSIONS)]
    media = [{'type': 'image', 'filename': f} for f in images] + \
             [{'type': 'video', 'filename': f} for f in videos]

    if request.method == 'POST':
        selected = request.form.get('media')
        if selected:
            current_app.config['SELECTED_IMAGE']['filename'] = selected
    selected = current_app.config['SELECTED_IMAGE']['filename']
    return render_template('select.html', media=media, selected=selected)


@main.route('/display')
def display():
    return render_template('display.html')


@main.route('/current_image')
def current_image():
    filename = current_app.config['SELECTED_IMAGE']['filename']
    if filename:
        ext = filename.split('.')[-1].lower()
        filetype = 'video' if ext in VIDEO_EXTENSIONS else 'image'
        return jsonify({
            "filename": f"/static/images/{filename}",
            "type": filetype
        })
    else:
        return jsonify({"filename": None, "type": None})
