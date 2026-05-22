from flask import Blueprint, abort, make_response
from models import get_character, get_all_characters
from export import (export_character, export_all, slugify,
                    export_character_markdown, export_all_markdown)

export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.route('/all')
def all_characters():
    payload = export_all()
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers['Content-Disposition'] = 'attachment; filename=swtor-all-characters.json'
    return resp


@export_bp.route('/<int:character_id>')
def single(character_id):
    char = get_character(character_id)
    if char is None:
        abort(404)
    payload = export_character(character_id)
    name_slug = slugify(char['name'])
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers['Content-Disposition'] = f'attachment; filename=swtor-{name_slug}.json'
    return resp


@export_bp.route('/all/markdown')
def all_characters_markdown():
    payload = export_all_markdown()
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'text/markdown; charset=utf-8'
    resp.headers['Content-Disposition'] = 'attachment; filename=swtor-all-characters.md'
    return resp


@export_bp.route('/<int:character_id>/markdown')
def single_markdown(character_id):
    char = get_character(character_id)
    if char is None:
        abort(404)
    payload = export_character_markdown(character_id)
    name_slug = slugify(char['name'])
    resp = make_response(payload)
    resp.headers['Content-Type'] = 'text/markdown; charset=utf-8'
    resp.headers['Content-Disposition'] = f'attachment; filename=swtor-{name_slug}.md'
    return resp
