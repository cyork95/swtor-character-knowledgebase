from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import (get_character, get_companions, create_influence_entry,
                    delete_influence_entry, get_influence_log)

influence_bp = Blueprint('influence', __name__)


def _safe_int(val, default=0):
    try:
        return int(val) if val else default
    except (ValueError, TypeError):
        return default


@influence_bp.route('/character/<int:cid>/influence/new', methods=['GET', 'POST'])
def add(cid):
    char = get_character(cid)
    if char is None:
        abort(404)
    companions = get_companions(cid)

    if request.method == 'POST':
        companion_name = request.form.get('companion_name', '').strip()
        change = _safe_int(request.form.get('influence_change'))
        if not companion_name:
            flash('Companion name is required.', 'error')
            return render_template('influence_form.html', char=char, companions=companions)
        if change == 0:
            flash('Influence change cannot be zero.', 'error')
            return render_template('influence_form.html', char=char, companions=companions)

        create_influence_entry({
            'character_id': cid,
            'companion_name': companion_name,
            'influence_change': change,
            'source': request.form.get('source', '').strip(),
            'notes': request.form.get('notes', '').strip(),
        })
        direction = 'gained' if change > 0 else 'lost'
        flash(f'{companion_name} {direction} {abs(change)} influence.', 'success')
        return redirect(url_for('characters.detail', cid=cid))

    # Pre-select companion if passed as query param
    preselect = request.args.get('companion', '')
    return render_template('influence_form.html', char=char,
                           companions=companions, preselect=preselect)


@influence_bp.route('/character/<int:cid>/influence/<int:eid>/delete', methods=['POST'])
def remove(cid, eid):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_influence_entry(eid)
    flash('Influence entry removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))
