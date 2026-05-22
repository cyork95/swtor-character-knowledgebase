from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import get_character, create_decision, delete_decision, create_tags
from db import get_db

decisions_bp = Blueprint('decisions', __name__)


def _recalculate_alignment(character_id):
    db = get_db()
    rows = db.execute(
        'SELECT alignment_impact, alignment_points FROM story_decisions WHERE character_id = ?',
        (character_id,)
    ).fetchall()
    light = sum(abs(r['alignment_points']) for r in rows if r['alignment_impact'] == 'LIGHT')
    dark = sum(abs(r['alignment_points']) for r in rows if r['alignment_impact'] == 'DARK')
    db.execute(
        'UPDATE characters SET light_side_pts = ?, dark_side_pts = ? WHERE id = ?',
        (light, dark, character_id)
    )
    db.commit()


@decisions_bp.route('/character/<int:cid>/decision', methods=['GET', 'POST'])
def log(cid):
    char = get_character(cid)
    if char is None:
        abort(404)

    if request.method == 'POST':
        choice = request.form.get('choice', '').strip()
        if not choice:
            flash('Decision text is required.', 'error')
            return render_template('decision_form.html', char=char)

        data = {
            'character_id': cid,
            'choice': choice,
            'context': request.form.get('context', '').strip(),
            'consequence': request.form.get('consequence', '').strip(),
            'alignment_impact': request.form.get('alignment_impact', 'NEUTRAL'),
            'alignment_points': _safe_int(request.form.get('alignment_points')),
            'companion_involved': request.form.get('companion_involved', '').strip(),
        }
        decision_id = create_decision(data)

        raw_tags = request.form.get('tags', '')
        tags = [t.strip() for t in raw_tags.split(',') if t.strip()]
        create_tags(decision_id, tags)

        _recalculate_alignment(cid)
        flash('Decision logged.', 'success')
        return redirect(url_for('characters.detail', cid=cid))

    return render_template('decision_form.html', char=char)


@decisions_bp.route('/character/<int:cid>/decision/<int:did>/delete', methods=['POST'])
def remove(cid, did):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_decision(did)
    _recalculate_alignment(cid)
    flash('Decision removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))


def _safe_int(val, default=0):
    try:
        return int(val) if val else default
    except (ValueError, TypeError):
        return default
