import json
import re
import uuid
from datetime import datetime, timezone

from models import (get_all_characters, get_character, get_decisions, get_companions, get_arcs,
                    get_alignment_rank, get_titles, get_planet_progress,
                    get_character_outfits, get_companion_outfits, get_journal_entries)


def slugify(text):
    if not text:
        return 'unknown'
    text = text.lower()
    text = re.sub(r"['\"]", '', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def to_sn_timestamp(sqlite_ts):
    if not sqlite_ts:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    try:
        dt = datetime.strptime(str(sqlite_ts), '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')


def _alignment_bar(light_pts, dark_pts):
    total = (light_pts or 0) + (dark_pts or 0)
    if total == 0:
        pct = 50
    else:
        pct = round((light_pts or 0) / total * 100)
    light_chars = round(pct / 100 * 20)
    dark_chars = 20 - light_chars
    bar = '█' * light_chars + '░' * dark_chars
    return f'LIGHT {bar} DARK  ({light_pts or 0} / {dark_pts or 0} pts, {pct}% Light Side)'


def format_note_text(character, decisions, companions, arcs):
    char = dict(character)
    lines = []

    lines.append(f'# {char["name"]}')
    lines.append('')

    lines.append('## Stats')
    cls = char.get('class') or '—'
    adv = char.get('advanced_class')
    lines.append(f'- **Class:** {cls}' + (f' / {adv}' if adv else ''))
    lines.append(f'- **Species:** {char.get("species") or "—"}  |  **Server:** {char.get("server") or "—"}')
    lines.append('')

    lines.append('## Alignment')
    lines.append(_alignment_bar(char.get('light_side_pts', 0), char.get('dark_side_pts', 0)))
    lines.append('')

    lines.append('## Story Progress')
    lines.append(f'- **Current Chapter:** {char.get("current_chapter") or "—"}')
    lines.append(f'- **Current Expansion:** {char.get("current_expansion") or "—"}')
    lines.append('')

    if arcs:
        lines.append('## Completed Story Arcs')
        for arc in arcs:
            a = dict(arc)
            lines.append(f'- {a.get("arc_name", "—")} ({a.get("expansion", "—")})')
        lines.append('')

    if decisions:
        lines.append('## Story Decisions')
        for dec in decisions:
            d = dict(dec)
            impact = d.get('alignment_impact', 'NEUTRAL')
            pts = d.get('alignment_points', 0)
            sign = '+' if impact in ('LIGHT', 'NEUTRAL') else '+'
            lines.append(f'### {impact} {sign}{pts} pts — {d.get("choice", "")}')
            if d.get('context'):
                lines.append(f'- **Context:** {d["context"]}')
            if d.get('consequence'):
                lines.append(f'- **Consequence:** {d["consequence"]}')
            extras = []
            if d.get('companion_involved'):
                extras.append(f'**Companion:** {d["companion_involved"]}')
            if d.get('tags'):
                extras.append(f'**Tags:** {d["tags"]}')
            if extras:
                lines.append('- ' + '  |  '.join(extras))
            lines.append('')

    if companions:
        lines.append('## Companions')
        lines.append('| Name | Status | Relationship | Romance |')
        lines.append('|------|--------|-------------|---------|')
        for comp in companions:
            c = dict(comp)
            romance = 'Yes' if c.get('is_romance') else 'No'
            lines.append(
                f'| {c.get("name", "—")} | {c.get("status", "—")} '
                f'| {c.get("relationship_level", 0)} | {romance} |'
            )
            if c.get('notable_interactions'):
                lines.append(f'  *{c["notable_interactions"]}*')
        lines.append('')

    if char.get('notes'):
        lines.append('## Notes')
        lines.append(char['notes'])
        lines.append('')

    return '\n'.join(lines)


def build_note_item(character, decisions, companions, arcs, note_uuid, tag_uuids):
    char = dict(character)
    cls = char.get('class') or ''
    title = f'SWTOR — {char["name"]}' + (f' ({cls})' if cls else '')
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    created = to_sn_timestamp(char.get('created_at'))
    updated = to_sn_timestamp(char.get('updated_at'))

    references = [{'uuid': tuid, 'content_type': 'Tag'} for tuid in tag_uuids]

    return {
        'uuid': note_uuid,
        'content_type': 'Note',
        'created_at': created,
        'updated_at': updated,
        'content': {
            'title': title,
            'text': format_note_text(character, decisions, companions, arcs),
            'references': references,
            'appData': {
                'org.standardnotes.sn': {'client_updated_at': now}
            },
        },
    }


def build_tag_item(tag_title, tag_uuid_str, note_uuids):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    references = [{'uuid': nuid, 'content_type': 'Note'} for nuid in note_uuids]
    return {
        'uuid': tag_uuid_str,
        'content_type': 'Tag',
        'created_at': now,
        'updated_at': now,
        'content': {
            'title': tag_title,
            'references': references,
        },
    }


def export_character(character_id):
    character = get_character(character_id)
    if character is None:
        return None
    decisions = get_decisions(character_id)
    companions = get_companions(character_id)
    arcs = get_arcs(character_id)

    note_uuid = str(uuid.uuid4())
    char = dict(character)
    cls_slug = slugify(char.get('class') or '')
    name_slug = slugify(char.get('name') or '')
    tag_titles = ['swtor', cls_slug, name_slug]

    tag_items = []
    tag_uuids = []
    for title in tag_titles:
        tuid = str(uuid.uuid4())
        tag_uuids.append(tuid)
        tag_items.append(build_tag_item(title, tuid, [note_uuid]))

    note_item = build_note_item(character, decisions, companions, arcs, note_uuid, tag_uuids)
    payload = {'version': '004', 'items': [note_item] + tag_items}
    return json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')


def export_all():
    characters = get_all_characters()
    tag_registry = {}
    note_items = []

    for character in characters:
        char_id = character['id']
        decisions = get_decisions(char_id)
        companions = get_companions(char_id)
        arcs = get_arcs(char_id)

        note_uuid = str(uuid.uuid4())
        char = dict(character)
        cls_slug = slugify(char.get('class') or '')
        name_slug = slugify(char.get('name') or '')

        note_tag_uuids = []
        for tag_title in ['swtor', cls_slug, name_slug]:
            if tag_title not in tag_registry:
                tag_registry[tag_title] = {'uuid': str(uuid.uuid4()), 'note_uuids': []}
            tag_registry[tag_title]['note_uuids'].append(note_uuid)
            note_tag_uuids.append(tag_registry[tag_title]['uuid'])

        note_items.append(
            build_note_item(character, decisions, companions, arcs, note_uuid, note_tag_uuids)
        )

    tag_items = [
        build_tag_item(title, info['uuid'], info['note_uuids'])
        for title, info in tag_registry.items()
    ]

    payload = {'version': '004', 'items': note_items + tag_items}
    return json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')


# ---------------------------------------------------------------------------
# Markdown Export
# ---------------------------------------------------------------------------

def _md_table(headers, rows):
    """Build a simple markdown table."""
    lines = []
    lines.append('| ' + ' | '.join(headers) + ' |')
    lines.append('| ' + ' | '.join('---' for _ in headers) + ' |')
    for row in rows:
        lines.append('| ' + ' | '.join(str(c) for c in row) + ' |')
    return '\n'.join(lines)


def format_markdown(character_id):
    """
    Render a single character as clean Markdown, including all new fields:
    crew skills, outfits, companion outfits, titles, planet progress,
    inventory notes, RP backstory, session journal.
    """
    character   = get_character(character_id)
    if character is None:
        return None

    char        = dict(character)
    decisions   = get_decisions(character_id)
    companions  = get_companions(character_id)
    arcs        = get_arcs(character_id)
    rank        = get_alignment_rank(char.get('light_side_pts', 0), char.get('dark_side_pts', 0))
    titles      = get_titles(character_id)
    planets     = get_planet_progress(character_id)
    outfits     = get_character_outfits(character_id)
    comp_outfits = get_companion_outfits(character_id)
    journal     = get_journal_entries(character_id)

    L = []
    hr = '---'

    # ── Header ──────────────────────────────────────────────────────────────
    cls = char.get('class') or ''
    adv = char.get('advanced_class') or ''
    class_str = cls + (f' / {adv}' if adv else '')
    legacy = char.get('legacy') or ''

    L.append(f'# {char["name"]}')
    subtitle_parts = [p for p in [class_str, char.get('species'), char.get('server')] if p]
    if legacy:
        subtitle_parts.append(f'{legacy} Legacy')
    L.append('*' + '  ·  '.join(subtitle_parts) + '*')
    L.append('')

    # ── Alignment ───────────────────────────────────────────────────────────
    L.append('## Alignment')
    L.append(f'**{rank["rank"]}** — Net {rank["net"]:+} pts')
    L.append('')
    L.append(_alignment_bar(char.get('light_side_pts', 0), char.get('dark_side_pts', 0)))
    L.append('')

    # ── Story Progress ───────────────────────────────────────────────────────
    L.append('## Story Progress')
    L.append(f'- **Expansion:** {char.get("current_expansion") or "—"}')
    L.append(f'- **Chapter:** {char.get("current_chapter") or "—"}')
    L.append('')

    # ── Crew Skills ──────────────────────────────────────────────────────────
    crew = [(char.get(f'crew_skill_{n}'), char.get(f'crew_skill_{n}_level', 1))
            for n in (1, 2, 3) if char.get(f'crew_skill_{n}')]
    if crew:
        L.append('## Crew Skills')
        for skill, level in crew:
            L.append(f'- {skill} (Level {level})')
        L.append('')

    # ── Titles ───────────────────────────────────────────────────────────────
    if titles:
        L.append('## Titles & Achievements')
        for t in titles:
            t = dict(t)
            line = f'- "{t["title"]}"'
            if t.get('earned_at'):
                line += f' — {t["earned_at"]}'
            if t.get('notes'):
                line += f'  \n  *{t["notes"]}*'
            L.append(line)
        L.append('')

    # ── Story Arcs ───────────────────────────────────────────────────────────
    if arcs:
        L.append('## Completed Story Arcs')
        for arc in arcs:
            a = dict(arc)
            L.append(f'- {a.get("arc_name", "—")} ({a.get("expansion", "—")})')
        L.append('')

    # ── Planet Progress ──────────────────────────────────────────────────────
    if planets:
        L.append('## Planet Progress')
        status_icon = {'complete': '✓', 'in_progress': '▶', 'not_started': '○'}
        rows = []
        for p in planets:
            p = dict(p)
            icon = status_icon.get(p['status'], '?')
            bonus = '✓' if p.get('bonus_series') else '—'
            dc    = '✓' if p.get('datacrons')    else '—'
            rows.append([f'{icon} {p["planet_name"]}', p['status'].replace('_', ' ').title(), bonus, dc])
        L.append(_md_table(['Planet', 'Status', 'Bonus Series', 'Datacrons'], rows))
        L.append('')

    # ── Story Decisions ──────────────────────────────────────────────────────
    if decisions:
        L.append(f'## Story Decisions ({len(decisions)})')
        for dec in decisions:
            d = dict(dec)
            impact = d.get('alignment_impact', 'NEUTRAL')
            pts    = d.get('alignment_points', 0)
            ts     = str(d.get('timestamp') or '')[:10]
            L.append(f'### {impact} +{pts} pts — {d.get("choice", "")}')
            if ts:
                L.append(f'*{ts}*')
            if d.get('context'):
                L.append(f'- **Context:** {d["context"]}')
            if d.get('consequence'):
                L.append(f'- **Consequence:** {d["consequence"]}')
            extras = []
            if d.get('companion_involved'):
                extras.append(f'**Companion:** {d["companion_involved"]}')
            if d.get('tags'):
                extras.append(f'**Tags:** {d["tags"]}')
            if extras:
                L.append('- ' + '  |  '.join(extras))
            L.append('')

    # ── Companions ───────────────────────────────────────────────────────────
    if companions:
        L.append('## Companions')
        rows = []
        for c in companions:
            c = dict(c)
            romance = '♥' if c.get('is_romance') else '—'
            rows.append([c.get('name', '—'), c.get('status', '—'),
                         str(c.get('relationship_level', 0)), romance])
        L.append(_md_table(['Name', 'Status', 'Base Influence', 'Romance'], rows))
        L.append('')

    # ── Outfits ──────────────────────────────────────────────────────────────
    _SLOT_LABELS = [('head','Head'), ('chest','Chest'), ('legs','Legs'),
                    ('hands','Hands'), ('feet','Feet'), ('waist','Waist'),
                    ('wrists','Wrists'), ('main_hand','Main Hand'),
                    ('off_hand','Off-Hand'), ('dye_module','Dye')]

    if outfits:
        L.append('## Outfits')
        for o in outfits:
            o = dict(o)
            active_marker = ' *(active)*' if o.get('is_active') else ''
            L.append(f'### {o.get("outfit_name", "Outfit")} — Slot {o.get("slot_number", 1)}{active_marker}')
            rows = [(label, o[slot]) for slot, label in _SLOT_LABELS if o.get(slot)]
            if rows:
                L.append(_md_table(['Slot', 'Item'], rows))
            if o.get('notes'):
                L.append(f'*{o["notes"]}*')
            L.append('')

    if comp_outfits:
        L.append('## Companion Outfits')
        for o in comp_outfits:
            o = dict(o)
            L.append(f'### {o.get("companion_name")} — {o.get("outfit_name", "Default")}')
            rows = [(label, o[slot]) for slot, label in _SLOT_LABELS if o.get(slot)]
            if rows:
                L.append(_md_table(['Slot', 'Item'], rows))
            if o.get('notes'):
                L.append(f'*{o["notes"]}*')
            L.append('')

    # ── Inventory Notes ──────────────────────────────────────────────────────
    if char.get('inventory_notes'):
        L.append('## Inventory Notes')
        L.append(char['inventory_notes'])
        L.append('')

    # ── RP Backstory ─────────────────────────────────────────────────────────
    rp_fields = [char.get(f) for f in ('rp_homeworld','rp_motivation','rp_personality',
                                        'rp_relationships','rp_backstory')]
    if any(rp_fields):
        L.append('## Backstory')
        if char.get('rp_homeworld'):
            L.append(f'**Homeworld:** {char["rp_homeworld"]}')
        if char.get('rp_motivation'):
            L.append(f'**Motivation:** {char["rp_motivation"]}')
        if char.get('rp_personality'):
            L.append(f'**Personality:** {char["rp_personality"]}')
        if char.get('rp_relationships'):
            L.append('')
            L.append('**Notable Relationships**')
            L.append(char['rp_relationships'])
        if char.get('rp_backstory'):
            L.append('')
            L.append(char['rp_backstory'])
        L.append('')

    # ── Session Journal ──────────────────────────────────────────────────────
    if journal:
        L.append(f'## Session Journal ({len(journal)} entries)')
        for entry in journal:
            e = dict(entry)
            date_str = f' — {e["session_date"]}' if e.get('session_date') else ''
            L.append(f'### {e.get("summary", "")}{date_str}')
            if e.get('notes'):
                L.append(e['notes'])
            L.append('')

    # ── Notes ────────────────────────────────────────────────────────────────
    if char.get('notes'):
        L.append('## Notes')
        L.append(char['notes'])
        L.append('')

    # ── Footer ───────────────────────────────────────────────────────────────
    generated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    L.append(hr)
    L.append(f'*Exported from SWTOR Character Knowledgebase — {generated}*')

    return '\n'.join(L)


def export_character_markdown(character_id):
    """Return UTF-8 encoded markdown bytes for a single character."""
    md = format_markdown(character_id)
    if md is None:
        return None
    return md.encode('utf-8')


def export_all_markdown():
    """Return UTF-8 encoded markdown bytes for all characters, one per section."""
    characters = get_all_characters()
    sections = []
    for char in characters:
        md = format_markdown(char['id'])
        if md:
            sections.append(md)
    generated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    header = f'# SWTOR Character Knowledgebase\n*Exported {generated}*\n\n---\n'
    return (header + '\n\n---\n\n'.join(sections)).encode('utf-8')
