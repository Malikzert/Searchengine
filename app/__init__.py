from flask import Flask, current_app

def create_app():
    app = Flask(__name__)
    
    # Konfigurasi dasar
    app.config['SECRET_KEY'] = 'secret-key-flask'

    # Agar current_app bisa digunakan di template
    @app.context_processor
    def inject_current_app():
        return dict(current_app=current_app)

    # Import dan daftarkan blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
