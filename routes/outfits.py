from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import (get_character, get_companions,
                    get_character_outfit, create_character_outfit,
                    update_character_outfit, delete_character_outfit,
                    set_active_outfit,
                    get_companion_outfit, create_companion_outfit,
                    update_companion_outfit, delete_companion_outfit)

outfits_bp = Blueprint('outfits', __name__)

_ARMOR_SLOTS = ['head', 'chest', 'legs', 'hands', 'feet', 'waist', 'wrists',
                'main_hand', 'off_hand', 'dye_module']


def _outfit_data_from_form(character_id):
    return {
        'character_id': character_id,
        'outfit_name': request.form.get('outfit_name', '').strip() or 'Outfit',
        'slot_number': _safe_int(request.form.get('slot_number'), 1),
        'is_active': 1 if request.form.get('is_active') else 0,
        **{slot: request.form.get(slot, '').strip() or None for slot in _ARMOR_SLOTS},
        'notes': request.form.get('notes', '').strip() or None,
    }


def _comp_outfit_data_from_form(character_id):
    return {
        'character_id': character_id,
        'companion_name': request.form.get('companion_name', '').strip(),
        'outfit_name': request.form.get('outfit_name', '').strip() or 'Default',
        **{slot: request.form.get(slot, '').strip() or None for slot in _ARMOR_SLOTS},
        'notes': request.form.get('notes', '').strip() or None,
    }


def _safe_int(val, default=1):
    try:
        return int(val) if val else default
    except (ValueError, TypeError):
        return default


# ── Character Outfits ───────────────────────────────────────────────────────

@outfits_bp.route('/character/<int:cid>/outfit/new', methods=['GET', 'POST'])
def add(cid):
    char = get_character(cid)
    if char is None:
        abort(404)
    if request.method == 'POST':
        data = _outfit_data_from_form(cid)
        create_character_outfit(data)
        flash('Outfit saved.', 'success')
        return redirect(url_for('characters.detail', cid=cid))
    return render_template('outfit_form.html', char=char, outfit=None,
                           slots=_ARMOR_SLOTS, form_title='Add Outfit',
                           action_url=url_for('outfits.add', cid=cid))


@outfits_bp.route('/character/<int:cid>/outfit/<int:oid>/edit', methods=['GET', 'POST'])
def edit(cid, oid):
    char = get_character(cid)
    outfit = get_character_outfit(oid)
    if char is None or outfit is None:
        abort(404)
    if request.method == 'POST':
        data = _outfit_data_from_form(cid)
        update_character_outfit(oid, data)
        flash('Outfit updated.', 'success')
        return redirect(url_for('characters.detail', cid=cid))
    return render_template('outfit_form.html', char=char, outfit=outfit,
                           slots=_ARMOR_SLOTS, form_title='Edit Outfit',
                           action_url=url_for('outfits.edit', cid=cid, oid=oid))


@outfits_bp.route('/character/<int:cid>/outfit/<int:oid>/activate', methods=['POST'])
def activate(cid, oid):
    char = get_character(cid)
    if char is None:
        abort(404)
    set_active_outfit(cid, oid)
    flash('Active outfit updated.', 'success')
    return redirect(url_for('characters.detail', cid=cid))


@outfits_bp.route('/character/<int:cid>/outfit/<int:oid>/delete', methods=['POST'])
def remove(cid, oid):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_character_outfit(oid)
    flash('Outfit removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))


# ── Companion Outfits ───────────────────────────────────────────────────────

@outfits_bp.route('/character/<int:cid>/companion-outfit/new', methods=['GET', 'POST'])
def add_companion(cid):
    char = get_character(cid)
    if char is None:
        abort(404)
    companions = get_companions(cid)
    preselect = request.args.get('companion', '')
    if request.method == 'POST':
        data = _comp_outfit_data_from_form(cid)
        if not data['companion_name']:
            flash('Companion name is required.', 'error')
            return render_template('companion_outfit_form.html', char=char,
                                   outfit=None, companions=companions,
                                   slots=_ARMOR_SLOTS, preselect=preselect,
                                   form_title='Add Companion Outfit',
                                   action_url=url_for('outfits.add_companion', cid=cid))
        create_companion_outfit(data)
        flash('Companion outfit saved.', 'success')
        return redirect(url_for('characters.detail', cid=cid))
    return render_template('companion_outfit_form.html', char=char, outfit=None,
                           companions=companions, slots=_ARMOR_SLOTS,
                           preselect=preselect,
                           form_title='Add Companion Outfit',
                           action_url=url_for('outfits.add_companion', cid=cid))


@outfits_bp.route('/character/<int:cid>/companion-outfit/<int:oid>/edit', methods=['GET', 'POST'])
def edit_companion(cid, oid):
    char = get_character(cid)
    outfit = get_companion_outfit(oid)
    if char is None or outfit is None:
        abort(404)
    companions = get_companions(cid)
    if request.method == 'POST':
        data = _comp_outfit_data_from_form(cid)
        update_companion_outfit(oid, data)
        flash('Companion outfit updated.', 'success')
        return redirect(url_for('characters.detail', cid=cid))
    return render_template('companion_outfit_form.html', char=char, outfit=outfit,
                           companions=companions, slots=_ARMOR_SLOTS,
                           preselect=outfit['companion_name'],
                           form_title='Edit Companion Outfit',
                           action_url=url_for('outfits.edit_companion', cid=cid, oid=oid))


@outfits_bp.route('/character/<int:cid>/companion-outfit/<int:oid>/delete', methods=['POST'])
def remove_companion(cid, oid):
    char = get_character(cid)
    if char is None:
        abort(404)
    delete_companion_outfit(oid)
    flash('Companion outfit removed.', 'success')
    return redirect(url_for('characters.detail', cid=cid))
