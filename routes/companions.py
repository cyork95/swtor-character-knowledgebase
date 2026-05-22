from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import get_character, get_companion, create_companion, update_companion, delete_companion

companions_bp = Blueprint('companions', __name__)

COMPANION_STATUSES = ['active', 'inactive', 'dead', 'romance', 'exiled']


def _safe_int(val, default=0):
    try:
        return int(val) if val else default
    except (ValueError, TypeError):
        return default


def _companion_data_from_form(cid):
    return {
        'character_id': cid,
        'name': request.form.get('name', '').strip(),
        'status': request.form.get('status', 'active'),
        'relationship_level': _safe_int(request.form.get('relationship_level')),
        'is_romance': 1 if request.form.get('is_romance') else 0,
        'notable_interactions': request.form.get('notable_interactions', '').strip(),
    }


@companions_bp.route('/character/<int:cid>/companion/new', methods=['GET', 'POST'])
def add(cid):
    char = get_character(cid)
    if char is None:
        abort(404)

    if request.method == 'POST':
        data = _companion_data_from_form(cid)
        if not data['name']:
            flash('Companion name is required.', 'error')
            return render_template('companion_form.html', char=char,
                                   companion=None, action='new',
                                   statuses=COMPANION_STATUSES)
        create_companion(data)
        flash(f'Companion "{data["name"]}" added.', 'success')
        return redirect(url_for('characters.detail', cid=cid))

    return render_template('companion_form.html', char=char,
                           companion=None, action='new',
                           statuses=COMPANION_STATUSES)


@companions_bp.route('/character/<int:cid>/companion/<int:coid>/edit', methods=['GET', 'POST'])
def edit(cid, coid):
    char = get_character(cid)
    companion = get_companion(coid)
    if char is None or companion is None:
        abort(404)

    if request.method == 'POST':
        data = _companion_data_from_form(cid)
        if not data['name']:
            flash('Companion name is required.', 'error')
            return render_template('companion_form.html', char=char,
                                   companion=companion, action='edit',
                                   statuses=COMPANION_STATUSES)
        update_companion(coid, data)
        flash(f'Companion "{data["name"]}" updated.', 'success')
        return redirect(url_for('characters.detail', cid=cid))

    return render_template('companion_form.html', char=char,
                           companion=companion, action='edit',
                           statuses=COMPANION_STATUSES)


@companions_bp.route('/character/<int:cid>/companion/<int:coid>/delete', methods=['POST'])
def remove(cid, coid):
    companion = get_companion(coid)
    if companion is None:
        abort(404)
    name = companion['name']
    delete_companion(coid)
    flash(f'Companion "{name}" removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))
