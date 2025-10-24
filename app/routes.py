import os
import json
from flask import Blueprint, current_app, render_template, jsonify, request, abort

main = Blueprint('main', __name__)

IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
VIDEO_EXTENSIONS = ('mp4', 'webm', 'mov')

# Path to the RFID map file (in project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RFID_MAP_PATH = os.path.join(PROJECT_ROOT, "rfid_map.json")

# Global caches
RFID_MEDIA_MAP = {}
current_tag = {"id": None}        # currently active RFID tag
previous_selection = {"filename": None}


def load_rfid_map():
    """Load RFID tag to media mapping from rfid_map.json."""
    global RFID_MEDIA_MAP
    try:
        with open(RFID_MAP_PATH, "r") as f:
            RFID_MEDIA_MAP = json.load(f)
        print(f"[INIT] Loaded RFID map from {RFID_MAP_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to load {RFID_MAP_PATH}: {e}")
        RFID_MEDIA_MAP = {}


# Load map once on module import
load_rfid_map()


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
            print(f"[WEB] Selected media: {selected}")

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


# =======================================
#  RFID Endpoints
# =======================================

@main.route('/rfid_event', methods=['POST'])
def rfid_event():
    """
    Receives RFID tag events from a remote reader.
    Expects JSON body:
      { "tag_id": "55E80705" }  -> tag present
      { "tag_id": null }        -> tag removed
    """
    data = request.get_json(silent=True) or {}
    tag_id = data.get("tag_id")

    # Tag removed → restore default
    if tag_id is None:
        default_file = RFID_MEDIA_MAP.get("default")
        current_tag["id"] = None
        if default_file:
            current_app.config['SELECTED_IMAGE']['filename'] = default_file
            print(f"[RFID] Tag removed → restored to default ({default_file})")
            return jsonify({"status": "reset", "default": default_file})
        else:
            print("[RFID] Tag removed, but no default defined.")
            return jsonify({"status": "no_default"})

    # Tag present
    tag_id = str(tag_id).strip().upper()
    current_tag["id"] = tag_id

    if tag_id not in RFID_MEDIA_MAP:
        print(f"[RFID] Unknown tag {tag_id}")
        return jsonify({"status": "unknown_tag", "tag_id": tag_id})

    filename = RFID_MEDIA_MAP[tag_id]
    media_path = os.path.join(current_app.config['IMAGE_FOLDER'], filename)

    if not os.path.exists(media_path):
        print(f"[RFID] File not found for tag {tag_id}: {filename}")
        return abort(404, f"File '{filename}' not found in {media_path}")

    current_app.config['SELECTED_IMAGE']['filename'] = filename
    print(f"[RFID] Tag {tag_id} → showing {filename}")
    return jsonify({"status": "ok", "tag_id": tag_id, "selected": filename})


@main.route('/reload_rfid_map', methods=['POST'])
def reload_rfid_map():
    """Manual endpoint to reload RFID map without restarting Flask."""
    load_rfid_map()
    return jsonify({"status": "reloaded", "map": RFID_MEDIA_MAP})


@main.route('/current_tag')
def get_current_tag():
    """
    Returns the currently active RFID tag and associated media (if any).
    Example response:
      {
        "tag_id": "55E80705",
        "media": "test2.jpg",
        "type": "image"
      }
    """
    tag_id = current_tag["id"]
    if not tag_id:
        return jsonify({"tag_id": None, "media": RFID_MEDIA_MAP.get("default"), "status": "no_tag"})

    media = RFID_MEDIA_MAP.get(tag_id)
    if not media:
        return jsonify({"tag_id": tag_id, "media": None, "status": "unknown_tag"})

    ext = media.split('.')[-1].lower()
    media_type = "video" if ext in VIDEO_EXTENSIONS else "image"
    return jsonify({
        "tag_id": tag_id,
        "media": media,
        "type": media_type,
        "status": "active"
    })
