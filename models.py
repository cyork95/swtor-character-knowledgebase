from db import get_db


# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------

def get_all_characters():
    db = get_db()
    return db.execute(
        'SELECT * FROM characters ORDER BY name ASC'
    ).fetchall()


def get_character(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM characters WHERE id = ?', (character_id,)
    ).fetchone()


def create_character(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO characters
           (name, class, advanced_class, species, server,
            level, light_side_pts, dark_side_pts, current_chapter, current_expansion, legacy, notes,
            crew_skill_1, crew_skill_1_level, crew_skill_2, crew_skill_2_level,
            crew_skill_3, crew_skill_3_level,
            inventory_notes, rp_homeworld, rp_motivation, rp_personality,
            rp_relationships, rp_backstory)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['name'], data.get('class'), data.get('advanced_class'),
         data.get('species'), data.get('server'),
         data.get('level', 1),
         data.get('light_side_pts', 0), data.get('dark_side_pts', 0),
         data.get('current_chapter'), data.get('current_expansion'),
         data.get('legacy'), data.get('notes'),
         data.get('crew_skill_1'), data.get('crew_skill_1_level', 1),
         data.get('crew_skill_2'), data.get('crew_skill_2_level', 1),
         data.get('crew_skill_3'), data.get('crew_skill_3_level', 1),
         data.get('inventory_notes'),
         data.get('rp_homeworld'), data.get('rp_motivation'),
         data.get('rp_personality'), data.get('rp_relationships'),
         data.get('rp_backstory'))
    )
    db.commit()
    return cursor.lastrowid


def update_character(character_id, data):
    db = get_db()
    db.execute(
        '''UPDATE characters SET
           name=?, class=?, advanced_class=?, species=?, server=?,
           level=?, light_side_pts=?, dark_side_pts=?,
           current_chapter=?, current_expansion=?, legacy=?, notes=?,
           crew_skill_1=?, crew_skill_1_level=?,
           crew_skill_2=?, crew_skill_2_level=?,
           crew_skill_3=?, crew_skill_3_level=?,
           inventory_notes=?,
           rp_homeworld=?, rp_motivation=?, rp_personality=?,
           rp_relationships=?, rp_backstory=?
           WHERE id=?''',
        (data['name'], data.get('class'), data.get('advanced_class'),
         data.get('species'), data.get('server'),
         data.get('level', 1),
         data.get('light_side_pts', 0), data.get('dark_side_pts', 0),
         data.get('current_chapter'), data.get('current_expansion'),
         data.get('legacy'), data.get('notes'),
         data.get('crew_skill_1'), data.get('crew_skill_1_level', 1),
         data.get('crew_skill_2'), data.get('crew_skill_2_level', 1),
         data.get('crew_skill_3'), data.get('crew_skill_3_level', 1),
         data.get('inventory_notes'),
         data.get('rp_homeworld'), data.get('rp_motivation'),
         data.get('rp_personality'), data.get('rp_relationships'),
         data.get('rp_backstory'),
         character_id)
    )
    db.commit()


def delete_character(character_id):
    db = get_db()
    db.execute('DELETE FROM characters WHERE id = ?', (character_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Story Arcs
# ---------------------------------------------------------------------------

def get_arcs(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM story_arcs WHERE character_id = ? ORDER BY completed_at ASC',
        (character_id,)
    ).fetchall()


def create_arc(data):
    db = get_db()
    cursor = db.execute(
        'INSERT INTO story_arcs (character_id, arc_name, expansion) VALUES (?, ?, ?)',
        (data['character_id'], data.get('arc_name'), data.get('expansion'))
    )
    db.commit()
    return cursor.lastrowid


def delete_arc(arc_id):
    db = get_db()
    db.execute('DELETE FROM story_arcs WHERE id = ?', (arc_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Story Decisions
# ---------------------------------------------------------------------------

def get_decisions(character_id):
    db = get_db()
    return db.execute(
        '''SELECT sd.*, GROUP_CONCAT(ct.tag, ', ') as tags
           FROM story_decisions sd
           LEFT JOIN choice_tags ct ON ct.decision_id = sd.id
           WHERE sd.character_id = ?
           GROUP BY sd.id
           ORDER BY sd.timestamp DESC''',
        (character_id,)
    ).fetchall()


def get_decision(decision_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM story_decisions WHERE id = ?', (decision_id,)
    ).fetchone()


def create_decision(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO story_decisions
           (character_id, choice, context, consequence,
            alignment_impact, alignment_points, companion_involved)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (data['character_id'], data['choice'], data.get('context'),
         data.get('consequence'), data.get('alignment_impact', 'NEUTRAL'),
         data.get('alignment_points', 0), data.get('companion_involved'))
    )
    db.commit()
    return cursor.lastrowid


def delete_decision(decision_id):
    db = get_db()
    db.execute('DELETE FROM story_decisions WHERE id = ?', (decision_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

def create_tags(decision_id, tags):
    if not tags:
        return
    db = get_db()
    db.executemany(
        'INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
        [(decision_id, tag) for tag in tags if tag.strip()]
    )
    db.commit()


def get_tags(decision_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM choice_tags WHERE decision_id = ?', (decision_id,)
    ).fetchall()


# ---------------------------------------------------------------------------
# Companions
# ---------------------------------------------------------------------------

def get_companions(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM companions WHERE character_id = ? ORDER BY name ASC',
        (character_id,)
    ).fetchall()


def get_companion(companion_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM companions WHERE id = ?', (companion_id,)
    ).fetchone()


def create_companion(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO companions
           (character_id, name, status, relationship_level, is_romance, notable_interactions)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (data['character_id'], data['name'], data.get('status', 'active'),
         data.get('relationship_level', 0), data.get('is_romance', 0),
         data.get('notable_interactions'))
    )
    db.commit()
    return cursor.lastrowid


def update_companion(companion_id, data):
    db = get_db()
    db.execute(
        '''UPDATE companions SET
           name=?, status=?, relationship_level=?, is_romance=?, notable_interactions=?
           WHERE id=?''',
        (data['name'], data.get('status', 'active'),
         data.get('relationship_level', 0), data.get('is_romance', 0),
         data.get('notable_interactions'), companion_id)
    )
    db.commit()


def delete_companion(companion_id):
    db = get_db()
    db.execute('DELETE FROM companions WHERE id = ?', (companion_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Cross-character query
# ---------------------------------------------------------------------------

def query_decisions(filters):
    db = get_db()
    needs_arcs_join = bool(filters.get('expansion'))

    sql = '''SELECT DISTINCT sd.*, c.name as char_name, c.class as char_class
             FROM story_decisions sd
             JOIN characters c ON sd.character_id = c.id'''

    if needs_arcs_join:
        sql += ' LEFT JOIN story_arcs sa ON sa.character_id = c.id'

    sql += ' WHERE 1=1'
    params = []

    if filters.get('alignment'):
        sql += ' AND sd.alignment_impact = ?'
        params.append(filters['alignment'].upper())

    if filters.get('companion'):
        sql += ' AND sd.companion_involved LIKE ?'
        params.append(f"%{filters['companion']}%")

    if filters.get('expansion'):
        sql += ' AND sa.expansion = ?'
        params.append(filters['expansion'])

    if filters.get('character_id'):
        sql += ' AND sd.character_id = ?'
        params.append(int(filters['character_id']))

    sql += ' ORDER BY sd.timestamp DESC'
    return db.execute(sql, params).fetchall()


# ---------------------------------------------------------------------------
# Alignment utilities
# ---------------------------------------------------------------------------

_RANK_THRESHOLDS = [
    (10000, 'LIGHT', 5), (7200, 'LIGHT', 4), (3600, 'LIGHT', 3),
    (1200, 'LIGHT', 2), (100,  'LIGHT', 1),
]
_ROMAN = ['', 'I', 'II', 'III', 'IV', 'V']


def get_alignment_rank(light_pts, dark_pts):
    """Return a dict describing the character's SWTOR alignment rank."""
    net = (light_pts or 0) - (dark_pts or 0)
    abs_net = abs(net)
    side = 'LIGHT' if net >= 0 else 'DARK'
    side_label = 'Light' if net >= 0 else 'Dark'

    for threshold, _, tier in _RANK_THRESHOLDS:
        if abs_net >= threshold:
            roman = _ROMAN[tier]
            return {
                'rank': f'{side_label} {roman}',
                'side': side,
                'tier': tier,
                'roman': roman,
                'net': net,
                'abs_net': abs_net,
            }

    return {'rank': 'Neutral', 'side': 'NEUTRAL', 'tier': 0, 'roman': '', 'net': net, 'abs_net': abs_net}


def get_alignment_history(character_id):
    """
    Return list of dicts showing running net alignment score after each decision,
    ordered chronologically. Used for the rank history chart.
    """
    db = get_db()
    rows = db.execute(
        '''SELECT alignment_impact, alignment_points, timestamp, choice
           FROM story_decisions WHERE character_id = ?
           ORDER BY timestamp ASC, id ASC''',
        (character_id,)
    ).fetchall()

    history = []
    running = 0
    for i, row in enumerate(rows):
        if row['alignment_impact'] == 'LIGHT':
            running += row['alignment_points'] or 0
        elif row['alignment_impact'] == 'DARK':
            running -= row['alignment_points'] or 0

        choice_text = row['choice'] or ''
        label = choice_text[:45] + '…' if len(choice_text) > 45 else choice_text
        ts = str(row['timestamp'] or '')[:10]

        history.append({
            'index': i + 1,
            'net': running,
            'label': label,
            'timestamp': ts,
            'impact': row['alignment_impact'],
        })

    return history


def get_moment_of_no_return(character_id):
    """
    Return the first decision (by index) where the running net alignment
    permanently crossed ±1200 (Light/Dark II threshold) and never returned.
    Returns None if the character never decisively committed.
    """
    history = get_alignment_history(character_id)
    if not history:
        return None

    final_net = history[-1]['net']

    # Determine which side the character ultimately settled on
    if final_net >= 1200:
        target_side = 'light'
        def crossed(net): return net >= 1200
    elif final_net <= -1200:
        target_side = 'dark'
        def crossed(net): return net <= -1200
    else:
        return None  # Still neutral / contested

    # Find first point that crossed and all subsequent stayed crossed
    for i, point in enumerate(history):
        if crossed(point['net']):
            if all(crossed(h['net']) for h in history[i:]):
                db = get_db()
                # Fetch full decision details for this point
                rows = db.execute(
                    '''SELECT * FROM story_decisions WHERE character_id = ?
                       ORDER BY timestamp ASC, id ASC LIMIT 1 OFFSET ?''',
                    (character_id, i)
                ).fetchone()
                return {
                    'decision_index': i + 1,
                    'net_at_crossing': point['net'],
                    'side': target_side,
                    'decision': dict(rows) if rows else None,
                    'label': point['label'],
                    'timestamp': point['timestamp'],
                }

    return None


# ---------------------------------------------------------------------------
# Influence log
# ---------------------------------------------------------------------------

def get_influence_log(character_id, companion_name=None):
    db = get_db()
    if companion_name:
        return db.execute(
            '''SELECT * FROM influence_log WHERE character_id = ? AND companion_name = ?
               ORDER BY logged_at DESC''',
            (character_id, companion_name)
        ).fetchall()
    return db.execute(
        'SELECT * FROM influence_log WHERE character_id = ? ORDER BY logged_at DESC',
        (character_id,)
    ).fetchall()


def get_companion_influence_totals(character_id):
    """Return {companion_name: total_influence_change} from the log."""
    db = get_db()
    rows = db.execute(
        '''SELECT companion_name, SUM(influence_change) as total
           FROM influence_log WHERE character_id = ?
           GROUP BY companion_name ORDER BY companion_name ASC''',
        (character_id,)
    ).fetchall()
    return {row['companion_name']: row['total'] for row in rows}


def create_influence_entry(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO influence_log
           (character_id, companion_name, influence_change, source, notes)
           VALUES (?, ?, ?, ?, ?)''',
        (data['character_id'], data['companion_name'],
         data['influence_change'], data.get('source'), data.get('notes'))
    )
    db.commit()
    return cursor.lastrowid


def delete_influence_entry(entry_id):
    db = get_db()
    db.execute('DELETE FROM influence_log WHERE id = ?', (entry_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Session journal
# ---------------------------------------------------------------------------

def get_journal_entries(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM session_journal WHERE character_id = ? ORDER BY created_at DESC',
        (character_id,)
    ).fetchall()


def create_journal_entry(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO session_journal (character_id, session_date, summary, notes)
           VALUES (?, ?, ?, ?)''',
        (data['character_id'], data.get('session_date'), data['summary'], data.get('notes'))
    )
    db.commit()
    return cursor.lastrowid


def delete_journal_entry(entry_id):
    db = get_db()
    db.execute('DELETE FROM session_journal WHERE id = ?', (entry_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Timeline (cross-character)
# ---------------------------------------------------------------------------

def get_timeline(limit=100):
    """All decisions across all characters, newest first."""
    db = get_db()
    return db.execute(
        '''SELECT sd.*, c.name as char_name, c.class as char_class, c.id as char_id
           FROM story_decisions sd
           JOIN characters c ON sd.character_id = c.id
           ORDER BY sd.timestamp DESC, sd.id DESC
           LIMIT ?''',
        (limit,)
    ).fetchall()


# ---------------------------------------------------------------------------
# Character Outfits
# ---------------------------------------------------------------------------

def get_character_outfits(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM character_outfits WHERE character_id = ? ORDER BY slot_number ASC',
        (character_id,)
    ).fetchall()


def get_character_outfit(outfit_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM character_outfits WHERE id = ?', (outfit_id,)
    ).fetchone()


def create_character_outfit(data):
    db = get_db()
    # Only one outfit can be active at a time
    if data.get('is_active'):
        db.execute(
            'UPDATE character_outfits SET is_active = 0 WHERE character_id = ?',
            (data['character_id'],)
        )
    cursor = db.execute(
        '''INSERT INTO character_outfits
           (character_id, outfit_name, slot_number, is_active,
            head, chest, legs, hands, feet, waist, wrists,
            main_hand, off_hand, dye_module, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['character_id'], data.get('outfit_name', 'Outfit'),
         data.get('slot_number', 1), 1 if data.get('is_active') else 0,
         data.get('head'), data.get('chest'), data.get('legs'),
         data.get('hands'), data.get('feet'), data.get('waist'),
         data.get('wrists'), data.get('main_hand'), data.get('off_hand'),
         data.get('dye_module'), data.get('notes'))
    )
    db.commit()
    return cursor.lastrowid


def update_character_outfit(outfit_id, data):
    db = get_db()
    if data.get('is_active'):
        # Fetch character_id first
        row = db.execute('SELECT character_id FROM character_outfits WHERE id = ?', (outfit_id,)).fetchone()
        if row:
            db.execute(
                'UPDATE character_outfits SET is_active = 0 WHERE character_id = ?',
                (row['character_id'],)
            )
    db.execute(
        '''UPDATE character_outfits SET
           outfit_name=?, slot_number=?, is_active=?,
           head=?, chest=?, legs=?, hands=?, feet=?, waist=?, wrists=?,
           main_hand=?, off_hand=?, dye_module=?, notes=?
           WHERE id=?''',
        (data.get('outfit_name', 'Outfit'), data.get('slot_number', 1),
         1 if data.get('is_active') else 0,
         data.get('head'), data.get('chest'), data.get('legs'),
         data.get('hands'), data.get('feet'), data.get('waist'),
         data.get('wrists'), data.get('main_hand'), data.get('off_hand'),
         data.get('dye_module'), data.get('notes'), outfit_id)
    )
    db.commit()


def delete_character_outfit(outfit_id):
    db = get_db()
    db.execute('DELETE FROM character_outfits WHERE id = ?', (outfit_id,))
    db.commit()


def set_active_outfit(character_id, outfit_id):
    db = get_db()
    db.execute(
        'UPDATE character_outfits SET is_active = 0 WHERE character_id = ?',
        (character_id,)
    )
    db.execute(
        'UPDATE character_outfits SET is_active = 1 WHERE id = ?',
        (outfit_id,)
    )
    db.commit()


# ---------------------------------------------------------------------------
# Companion Outfits
# ---------------------------------------------------------------------------

def get_companion_outfits(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM companion_outfits WHERE character_id = ? ORDER BY companion_name ASC',
        (character_id,)
    ).fetchall()


def get_companion_outfit(outfit_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM companion_outfits WHERE id = ?', (outfit_id,)
    ).fetchone()


def create_companion_outfit(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO companion_outfits
           (character_id, companion_name, outfit_name,
            head, chest, legs, hands, feet, waist, wrists,
            main_hand, off_hand, dye_module, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['character_id'], data['companion_name'],
         data.get('outfit_name', 'Default'),
         data.get('head'), data.get('chest'), data.get('legs'),
         data.get('hands'), data.get('feet'), data.get('waist'),
         data.get('wrists'), data.get('main_hand'), data.get('off_hand'),
         data.get('dye_module'), data.get('notes'))
    )
    db.commit()
    return cursor.lastrowid


def update_companion_outfit(outfit_id, data):
    db = get_db()
    db.execute(
        '''UPDATE companion_outfits SET
           companion_name=?, outfit_name=?,
           head=?, chest=?, legs=?, hands=?, feet=?, waist=?, wrists=?,
           main_hand=?, off_hand=?, dye_module=?, notes=?
           WHERE id=?''',
        (data['companion_name'], data.get('outfit_name', 'Default'),
         data.get('head'), data.get('chest'), data.get('legs'),
         data.get('hands'), data.get('feet'), data.get('waist'),
         data.get('wrists'), data.get('main_hand'), data.get('off_hand'),
         data.get('dye_module'), data.get('notes'), outfit_id)
    )
    db.commit()


def delete_companion_outfit(outfit_id):
    db = get_db()
    db.execute('DELETE FROM companion_outfits WHERE id = ?', (outfit_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Planet Progress
# ---------------------------------------------------------------------------

def get_planet_progress(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM planet_progress WHERE character_id = ? ORDER BY planet_name ASC',
        (character_id,)
    ).fetchall()


def get_planet_entry(planet_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM planet_progress WHERE id = ?', (planet_id,)
    ).fetchone()


def create_planet_entry(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO planet_progress
           (character_id, planet_name, status, bonus_series, datacrons, notes)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (data['character_id'], data['planet_name'],
         data.get('status', 'in_progress'),
         1 if data.get('bonus_series') else 0,
         1 if data.get('datacrons') else 0,
         data.get('notes'))
    )
    db.commit()
    return cursor.lastrowid


def update_planet_entry(planet_id, data):
    db = get_db()
    db.execute(
        '''UPDATE planet_progress SET
           planet_name=?, status=?, bonus_series=?, datacrons=?, notes=?
           WHERE id=?''',
        (data['planet_name'], data.get('status', 'in_progress'),
         1 if data.get('bonus_series') else 0,
         1 if data.get('datacrons') else 0,
         data.get('notes'), planet_id)
    )
    db.commit()


def delete_planet_entry(planet_id):
    db = get_db()
    db.execute('DELETE FROM planet_progress WHERE id = ?', (planet_id,))
    db.commit()


# ---------------------------------------------------------------------------
# Character Titles
# ---------------------------------------------------------------------------

def get_titles(character_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM character_titles WHERE character_id = ? ORDER BY id ASC',
        (character_id,)
    ).fetchall()


def create_title(data):
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO character_titles (character_id, title, earned_at, notes)
           VALUES (?, ?, ?, ?)''',
        (data['character_id'], data['title'],
         data.get('earned_at'), data.get('notes'))
    )
    db.commit()
    return cursor.lastrowid


def delete_title(title_id):
    db = get_db()
    db.execute('DELETE FROM character_titles WHERE id = ?', (title_id,))
    db.commit()
