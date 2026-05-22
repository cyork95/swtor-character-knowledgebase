import os
from flask import Flask
from db import init_db, close_db
from routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'swtor-dev-secret-change-in-prod')

    app.teardown_appcontext(close_db)

    register_blueprints(app)

    @app.template_filter('alignment_pct')
    def alignment_pct_filter(light, dark):
        total = (light or 0) + (dark or 0)
        return 50 if total == 0 else round((light or 0) / total * 100)

    @app.template_filter('impact_class')
    def impact_class_filter(impact):
        return (impact or 'neutral').lower()

    return app


# Initialize DB on first import (safe — all IF NOT EXISTS)
init_db()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
