from .characters import characters_bp
from .decisions import decisions_bp
from .companions import companions_bp
from .export import export_bp
from .arcs import arcs_bp
from .influence import influence_bp
from .journal import journal_bp
from .outfits import outfits_bp
from .titles import titles_bp
from .planets import planets_bp


def register_blueprints(app):
    app.register_blueprint(characters_bp)
    app.register_blueprint(decisions_bp)
    app.register_blueprint(companions_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(arcs_bp)
    app.register_blueprint(influence_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(outfits_bp)
    app.register_blueprint(titles_bp)
    app.register_blueprint(planets_bp)
