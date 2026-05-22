from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import get_character, create_title, delete_title

titles_bp = Blueprint('titles', __name__)


@titles_bp.route('/character/<int:cid>/title/new', methods=['GET', 'POST'])
def add(cid):
    char = get_character(cid)
    if char is None:
        abort(404)
    if request.method == 'POST':
        title_text = request.form.get('title', '').strip()
        if not title_text:
            flash('Title text is required.', 'error')
            return render_template('title_form.html', char=char,
                                   action_url=url_for('titles.add', cid=cid))
        create_title({
            'character_id': cid,
            'title': title_text,
            'earned_at': request.form.get('earned_at', '').strip() or None,
            'notes': request.form.get('notes', '').strip() or None,
        })
        flash('Title added.', 'success')
        return redirect(url_for('characters.detail', cid=cid))
    return render_template('title_form.html', char=char,
                           action_url=url_for('titles.add', cid=cid))


@titles_bp.route('/character/<int:cid>/title/<int:tid>/delete', methods=['POST'])
def remove(cid, tid):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_title(tid)
    flash('Title removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))
