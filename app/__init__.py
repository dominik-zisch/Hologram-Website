from flask import Flask

# Global variable to hold selected image
selected_image = {"filename": None}

def create_app():
    app = Flask(__name__)
    app.config['IMAGE_FOLDER'] = 'app/static/images'
    app.config['SELECTED_IMAGE'] = selected_image

    from .routes import main
    app.register_blueprint(main)

    return app
