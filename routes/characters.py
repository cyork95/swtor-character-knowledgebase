from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import (get_all_characters, get_character, create_character,
                    update_character, delete_character, get_decisions,
                    get_companions, get_arcs, query_decisions,
                    get_alignment_rank, get_alignment_history,
                    get_moment_of_no_return, get_influence_log,
                    get_companion_influence_totals, get_journal_entries,
                    get_timeline, get_character_outfits, get_companion_outfits,
                    get_titles, get_planet_progress)

characters_bp = Blueprint('characters', __name__)

SWTOR_CLASSES = [
    'Jedi Knight', 'Jedi Consular', 'Smuggler', 'Trooper',
    'Sith Warrior', 'Sith Inquisitor', 'Bounty Hunter', 'Imperial Agent',
]

SWTOR_SPECIES = [
    'Human', 'Twi\'lek', 'Zabrak', 'Miraluka', 'Mirialan',
    'Rattataki', 'Sith Pureblood', 'Chiss', 'Cyborg', 'Cathar',
    'Togruta', 'Nautolan', 'Nautolan',
]

SWTOR_SERVERS = [
    'Star Forge', 'Satele Shan', 'Darth Malgus', 'Tulak Hord', 'The Leviathan',
]

SWTOR_EXPANSIONS = [
    'Base Game', 'Rise of the Hutt Cartel', 'Shadow of Revan',
    'Knights of the Fallen Empire', 'Knights of the Eternal Throne',
    'Onslaught', 'Legacy of the Sith',
]


def _safe_int(val, default=0):
    try:
        return int(val) if val else default
    except (ValueError, TypeError):
        return default


SWTOR_CREW_SKILLS = [
    # Crafting
    'Armormech', 'Armstech', 'Artifice', 'Biochem', 'Cybertech', 'Synthweaving',
    # Gathering
    'Archaeology', 'Bioanalysis', 'Scavenging', 'Slicing',
    # Mission
    'Diplomacy', 'Investigation', 'Treasure Hunting', 'Underworld Trading',
]


def _char_data_from_form():
    return {
        'name':             request.form.get('name', '').strip(),
        'class':            request.form.get('class', '').strip(),
        'advanced_class':   request.form.get('advanced_class', '').strip(),
        'species':          request.form.get('species', '').strip(),
        'server':           request.form.get('server', '').strip(),
        'light_side_pts':   _safe_int(request.form.get('light_side_pts')),
        'dark_side_pts':    _safe_int(request.form.get('dark_side_pts')),
        'current_chapter':  request.form.get('current_chapter', '').strip(),
        'current_expansion':request.form.get('current_expansion', '').strip(),
        'legacy':           request.form.get('legacy', '').strip(),
        'notes':            request.form.get('notes', '').strip(),
        # Crew skills
        'crew_skill_1':       request.form.get('crew_skill_1', '').strip() or None,
        'crew_skill_1_level': _safe_int(request.form.get('crew_skill_1_level'), 1),
        'crew_skill_2':       request.form.get('crew_skill_2', '').strip() or None,
        'crew_skill_2_level': _safe_int(request.form.get('crew_skill_2_level'), 1),
        'crew_skill_3':       request.form.get('crew_skill_3', '').strip() or None,
        'crew_skill_3_level': _safe_int(request.form.get('crew_skill_3_level'), 1),
        # Inventory & RP
        'inventory_notes':  request.form.get('inventory_notes', '').strip() or None,
        'rp_homeworld':     request.form.get('rp_homeworld', '').strip() or None,
        'rp_motivation':    request.form.get('rp_motivation', '').strip() or None,
        'rp_personality':   request.form.get('rp_personality', '').strip() or None,
        'rp_relationships': request.form.get('rp_relationships', '').strip() or None,
        'rp_backstory':     request.form.get('rp_backstory', '').strip() or None,
    }


@characters_bp.route('/')
def dashboard():
    characters = get_all_characters()
    return render_template('dashboard.html', characters=characters)


@characters_bp.route('/character/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        data = _char_data_from_form()
        if not data['name']:
            flash('Character name is required.', 'error')
            return render_template('character_form.html', char=None,
                                   form_title='New Character',
                                   action_url=url_for('characters.create'),
                                   classes=SWTOR_CLASSES, species=SWTOR_SPECIES,
                                   servers=SWTOR_SERVERS, expansions=SWTOR_EXPANSIONS,
                                   crew_skills=SWTOR_CREW_SKILLS)
        char_id = create_character(data)
        flash(f'Character "{data["name"]}" created.', 'success')
        return redirect(url_for('characters.detail', cid=char_id))

    return render_template('character_form.html', char=None,
                           form_title='New Character',
                           action_url=url_for('characters.create'),
                           classes=SWTOR_CLASSES, species=SWTOR_SPECIES,
                           servers=SWTOR_SERVERS, expansions=SWTOR_EXPANSIONS,
                           crew_skills=SWTOR_CREW_SKILLS)


@characters_bp.route('/character/<int:cid>')
def detail(cid):
    char = get_character(cid)
    if char is None:
        abort(404)
    decisions   = get_decisions(cid)
    companions  = get_companions(cid)
    arcs        = get_arcs(cid)
    rank             = get_alignment_rank(char['light_side_pts'], char['dark_side_pts'])
    history          = get_alignment_history(cid)
    moment           = get_moment_of_no_return(cid)
    influence        = get_influence_log(cid)
    inf_totals       = get_companion_influence_totals(cid)
    journal          = get_journal_entries(cid)
    outfits          = get_character_outfits(cid)
    companion_outfits = get_companion_outfits(cid)
    titles           = get_titles(cid)
    planets          = get_planet_progress(cid)

    # Collect unique tags from all decisions for the filter UI
    all_tags = sorted({
        tag.strip()
        for dec in decisions
        if dec['tags']
        for tag in dec['tags'].split(',')
        if tag.strip()
    })

    # Planet stats summary
    planet_stats = {
        'complete':     sum(1 for p in planets if p['status'] == 'complete'),
        'in_progress':  sum(1 for p in planets if p['status'] == 'in_progress'),
        'total':        len(planets),
    }

    return render_template('character_detail.html',
                           char=char, decisions=decisions,
                           companions=companions, arcs=arcs,
                           rank=rank, history=history, moment=moment,
                           influence=influence, inf_totals=inf_totals,
                           journal=journal, all_tags=all_tags,
                           outfits=outfits, companion_outfits=companion_outfits,
                           titles=titles, planets=planets,
                           planet_stats=planet_stats)


@characters_bp.route('/character/<int:cid>/edit', methods=['GET', 'POST'])
def edit(cid):
    char = get_character(cid)
    if char is None:
        abort(404)

    if request.method == 'POST':
        data = _char_data_from_form()
        if not data['name']:
            flash('Character name is required.', 'error')
            return render_template('character_form.html', char=char,
                                   form_title=f'Edit — {char["name"]}',
                                   action_url=url_for('characters.edit', cid=cid),
                                   classes=SWTOR_CLASSES, species=SWTOR_SPECIES,
                                   servers=SWTOR_SERVERS, expansions=SWTOR_EXPANSIONS,
                                   crew_skills=SWTOR_CREW_SKILLS)
        update_character(cid, data)
        flash('Character updated.', 'success')
        return redirect(url_for('characters.detail', cid=cid))

    return render_template('character_form.html', char=char,
                           form_title=f'Edit — {char["name"]}',
                           action_url=url_for('characters.edit', cid=cid),
                           classes=SWTOR_CLASSES, species=SWTOR_SPECIES,
                           servers=SWTOR_SERVERS, expansions=SWTOR_EXPANSIONS,
                           crew_skills=SWTOR_CREW_SKILLS)


@characters_bp.route('/character/<int:cid>/delete', methods=['POST'])
def delete(cid):
    char = get_character(cid)
    if char is None:
        abort(404)
    name = char['name']
    delete_character(cid)
    flash(f'Character "{name}" deleted.', 'success')
    return redirect(url_for('characters.dashboard'))


@characters_bp.route('/query', methods=['GET', 'POST'])
def query():
    results = []
    filters = {}
    all_chars = get_all_characters()

    if request.method == 'POST':
        for key in ('alignment', 'companion', 'expansion', 'character_id'):
            val = request.form.get(key, '').strip()
            if val:
                filters[key] = val
        results = query_decisions(filters)

    return render_template('query.html',
                           results=results, filters=filters,
                           all_chars=all_chars, expansions=SWTOR_EXPANSIONS,
                           submitted=request.method == 'POST')


@characters_bp.route('/timeline')
def timeline():
    limit = _safe_int(request.args.get('limit'), default=200)
    entries = get_timeline(limit=limit)
    return render_template('timeline.html', entries=entries, limit=limit)


@characters_bp.route('/compare')
def compare():
    all_chars = get_all_characters()
    cid_a = _safe_int(request.args.get('a'))
    cid_b = _safe_int(request.args.get('b'))

    char_a = char_b = None
    rank_a = rank_b = None
    decisions_a = decisions_b = []
    companions_a = companions_b = []
    arcs_a = arcs_b = []

    if cid_a:
        char_a = get_character(cid_a)
        if char_a:
            rank_a      = get_alignment_rank(char_a['light_side_pts'], char_a['dark_side_pts'])
            decisions_a = get_decisions(cid_a)
            companions_a = get_companions(cid_a)
            arcs_a      = get_arcs(cid_a)

    if cid_b:
        char_b = get_character(cid_b)
        if char_b:
            rank_b      = get_alignment_rank(char_b['light_side_pts'], char_b['dark_side_pts'])
            decisions_b = get_decisions(cid_b)
            companions_b = get_companions(cid_b)
            arcs_b      = get_arcs(cid_b)

    return render_template('compare.html',
                           all_chars=all_chars,
                           cid_a=cid_a, cid_b=cid_b,
                           char_a=char_a, char_b=char_b,
                           rank_a=rank_a, rank_b=rank_b,
                           decisions_a=decisions_a, decisions_b=decisions_b,
                           companions_a=companions_a, companions_b=companions_b,
                           arcs_a=arcs_a, arcs_b=arcs_b)
