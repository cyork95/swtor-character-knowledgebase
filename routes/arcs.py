from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import get_character, get_arcs, create_arc, delete_arc

arcs_bp = Blueprint('arcs', __name__)

SWTOR_EXPANSIONS = [
    'Base Game', 'Rise of the Hutt Cartel', 'Shadow of Revan',
    'Knights of the Fallen Empire', 'Knights of the Eternal Throne',
    'Onslaught', 'Legacy of the Sith',
]


@arcs_bp.route('/character/<int:cid>/arc/new', methods=['GET', 'POST'])
def add(cid):
    char = get_character(cid)
    if char is None:
        abort(404)

    if request.method == 'POST':
        arc_name = request.form.get('arc_name', '').strip()
        if not arc_name:
            flash('Arc name is required.', 'error')
            return render_template('arc_form.html', char=char, expansions=SWTOR_EXPANSIONS)
        create_arc({
            'character_id': cid,
            'arc_name': arc_name,
            'expansion': request.form.get('expansion', '').strip(),
        })
        flash(f'Arc "{arc_name}" added.', 'success')
        return redirect(url_for('characters.detail', cid=cid))

    return render_template('arc_form.html', char=char, expansions=SWTOR_EXPANSIONS)


@arcs_bp.route('/character/<int:cid>/arc/<int:aid>/delete', methods=['POST'])
def remove(cid, aid):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_arc(aid)
    flash('Arc removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))
