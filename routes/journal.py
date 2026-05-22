from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import get_character, create_journal_entry, delete_journal_entry

journal_bp = Blueprint('journal', __name__)


@journal_bp.route('/character/<int:cid>/journal/new', methods=['GET', 'POST'])
def add(cid):
    char = get_character(cid)
    if char is None:
        abort(404)

    if request.method == 'POST':
        summary = request.form.get('summary', '').strip()
        if not summary:
            flash('Session summary is required.', 'error')
            return render_template('journal_form.html', char=char)

        create_journal_entry({
            'character_id': cid,
            'session_date': request.form.get('session_date', '').strip(),
            'summary': summary,
            'notes': request.form.get('notes', '').strip(),
        })
        flash('Session entry logged.', 'success')
        return redirect(url_for('characters.detail', cid=cid))

    return render_template('journal_form.html', char=char)


@journal_bp.route('/character/<int:cid>/journal/<int:jid>/delete', methods=['POST'])
def remove(cid, jid):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_journal_entry(jid)
    flash('Journal entry removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))
