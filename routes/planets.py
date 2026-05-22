from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import (get_character, get_planet_entry,
                    create_planet_entry, update_planet_entry, delete_planet_entry)

planets_bp = Blueprint('planets', __name__)

SWTOR_PLANETS = [
    # Starter worlds
    'Tython', 'Korriban', 'Ord Mantell', 'Hutta',
    # Core worlds
    'Coruscant', 'Dromund Kaas',
    # Mid-game
    'Taris', 'Balmorra', 'Nar Shaddaa', 'Tatooine', 'Alderaan',
    'Quesh', 'Hoth',
    # Late base game
    'Belsavis', 'Voss', 'Corellia', 'Ilum',
    # Expansions
    'Makeb', 'CZ-198', 'Oricon',
    'Rishi', 'Yavin 4', 'Ziost',
    'Asylum', 'Zakuul', 'Darvannis', 'Odessen', 'Arcann',
    'Iokath', 'Umbara', 'Copero', 'Nathema',
    'Ossus', 'Dantooine',
    'Onderon', 'Mek-Sha', 'Corellia (Onslaught)',
    'Manaan', 'Elom', 'Ruhnuk', 'Voss (Wrath)',
]


def _planet_data_from_form(character_id):
    return {
        'character_id': character_id,
        'planet_name': request.form.get('planet_name', '').strip(),
        'status': request.form.get('status', 'in_progress'),
        'bonus_series': 1 if request.form.get('bonus_series') else 0,
        'datacrons': 1 if request.form.get('datacrons') else 0,
        'notes': request.form.get('notes', '').strip() or None,
    }


@planets_bp.route('/character/<int:cid>/planet/new', methods=['GET', 'POST'])
def add(cid):
    char = get_character(cid)
    if char is None:
        abort(404)
    if request.method == 'POST':
        data = _planet_data_from_form(cid)
        if not data['planet_name']:
            flash('Planet name is required.', 'error')
            return render_template('planet_form.html', char=char, planet=None,
                                   planets=SWTOR_PLANETS,
                                   action_url=url_for('planets.add', cid=cid))
        create_planet_entry(data)
        flash(f'{data["planet_name"]} added.', 'success')
        return redirect(url_for('characters.detail', cid=cid))
    return render_template('planet_form.html', char=char, planet=None,
                           planets=SWTOR_PLANETS,
                           action_url=url_for('planets.add', cid=cid))


@planets_bp.route('/character/<int:cid>/planet/<int:pid>/edit', methods=['GET', 'POST'])
def edit(cid, pid):
    char = get_character(cid)
    planet = get_planet_entry(pid)
    if char is None or planet is None:
        abort(404)
    if request.method == 'POST':
        data = _planet_data_from_form(cid)
        update_planet_entry(pid, data)
        flash('Planet updated.', 'success')
        return redirect(url_for('characters.detail', cid=cid))
    return render_template('planet_form.html', char=char, planet=planet,
                           planets=SWTOR_PLANETS,
                           action_url=url_for('planets.edit', cid=cid, pid=pid))


@planets_bp.route('/character/<int:cid>/planet/<int:pid>/delete', methods=['POST'])
def remove(cid, pid):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_planet_entry(pid)
    flash('Planet removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))
