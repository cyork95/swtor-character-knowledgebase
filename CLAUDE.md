# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Start the dev server (http://127.0.0.1:5000)
python app.py

# Seed the database with two demo characters (Aria Solaris + Darth Vexus)
# Guard: exits without inserting if any characters already exist
python seed.py
```

No build step, no test suite, no linter config — this is an intentionally simple local tool.

## Database

- **Location:** `~/swtor-tracker/swtor.db` (resolved via `pathlib.Path.home()`)
- **Schema init:** `init_db()` in `db.py` is called at module level in `app.py` — safe to call repeatedly (all `IF NOT EXISTS`)
- **`PRAGMA foreign_keys=ON` is per-connection** — set in both `init_db()` and `get_db()` separately
- **WAL mode** is enabled for the connection
- **Adding columns to live DB:** use `ALTER TABLE ... ADD COLUMN` (SQLite does not support DROP COLUMN). Update both the `_SCHEMA` DDL in `db.py` and every affected `INSERT`/`UPDATE` in `models.py`.

### Schema (7 tables)

| Table | Purpose |
|---|---|
| `characters` | Core character sheet including `legacy`, `light_side_pts`, `dark_side_pts` |
| `story_decisions` | Individual choices; `alignment_impact IN ('LIGHT','DARK','NEUTRAL')`, `alignment_points` is positive magnitude only |
| `choice_tags` | Many-to-one tags for decisions (fetched via `GROUP_CONCAT` in `get_decisions`) |
| `companions` | Status `IN ('active','inactive','dead','romance','exiled')`, `is_romance` boolean |
| `story_arcs` | Completed expansion story arcs per character |
| `influence_log` | Companion influence change events (separate from base `relationship_level`) |
| `session_journal` | Free-form play session notes |

## Architecture

```
app.py              Flask factory; registers blueprints; registers two Jinja2 filters
db.py               SQLite connection lifecycle (get_db / close_db / init_db)
models.py           All SQL — returns sqlite3.Row; no Flask imports
export.py           Standard Notes export logic — no Flask imports
routes/
  __init__.py       register_blueprints() wires all 7 blueprints
  characters.py     /, /character/*, /query, /timeline, /compare
  decisions.py      Decision log/delete + _recalculate_alignment()
  companions.py     Companion CRUD
  arcs.py           Arc add/delete
  influence.py      Influence log add/delete
  journal.py        Session journal add/delete
  export.py         /export/<id> and /export/all — thin HTTP wrapper over export.py
templates/          Jinja2; all extend base.html
static/css/         Single file: style.css (CSS custom properties, no framework)
static/js/          Single file: main.js (vanilla JS, no framework)
```

## Key Conventions

**Alignment recalculation** — always recalculate from scratch (never increment):
```python
# In routes/decisions.py — called after every create or delete
_recalculate_alignment(character_id)
# Sums all LIGHT rows → light_side_pts, all DARK rows → dark_side_pts
```

**`alignment_points` sign convention** — store positive magnitude only; direction comes from `alignment_impact`. Net score for display = `light_side_pts - dark_side_pts`.

**Alignment rank thresholds** (defined in `models.py` as `_RANK_THRESHOLDS`):
`±100 = I`, `±1200 = II`, `±3600 = III`, `±7200 = IV`, `±10000 = V`

**Jinja2 filters** (registered in `app.py`):
- `{{ light | alignment_pct(dark) }}` → integer 0–100
- `{{ impact | impact_class }}` → `'light'`, `'dark'`, or `'neutral'`

**`sqlite3.Row` gotcha** — does not support `**row` spread; use `dict(row)` when you need to unpack.

**Checkbox handling** — `1 if request.form.get('is_romance') else 0` (absent when unchecked).

## Jinja2 Template Notes

- Decision entries carry `data-text` and `data-tags` attributes for client-side filtering in `main.js`
- The alignment history SVG chart is rendered entirely in Jinja2 math — no JavaScript
- `data-confirm="..."` on `<form>` triggers a JS confirm dialog before submit (handled in `main.js`)
- All deletes use `POST` forms (no `DELETE` method)

## Standard Notes Export

`export.py` produces v004 unencrypted backup JSON. Each character becomes one `Note` item linked to `Tag` items (`swtor`, class-slug, name-slug). The bulk export (`export_all`) deduplicates tags via a `tag_registry` dict. Output is `json.dumps(..., ensure_ascii=False).encode('utf-8')` to preserve Unicode alignment bar characters (`█`, `░`).
