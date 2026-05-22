import json
import re
import uuid
from datetime import datetime, timezone

from models import get_all_characters, get_character, get_decisions, get_companions, get_arcs


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
