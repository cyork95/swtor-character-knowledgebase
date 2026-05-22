# SWTOR Character Knowledgebase

A local web application for tracking Star Wars: The Old Republic characters — story decisions, alignment, companions, and story progression. Built with Python/Flask and SQLite.

## Prerequisites

- Python 3.10+
- Flask 3.x (`pip install flask`)

## Running the App

```bash
cd "SWTOR Character Knowledgebase"
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

The database is created automatically at `~/swtor-tracker/swtor.db` on first run.

## Loading Sample Data

With the app stopped (or in a second terminal):

```bash
python seed.py
```

This loads two example characters — Aria Solaris (Jedi Knight) and Darth Vexus (Sith Inquisitor) — with decisions, companions, and story arcs. Running it twice is safe; it skips if characters already exist.

To reset the database: delete `~/swtor-tracker/swtor.db` and re-run `python app.py` followed by `python seed.py`.

## Project Structure

```
SWTOR Character Knowledgebase/
├── app.py              Flask application factory + startup
├── db.py               SQLite connection, schema init
├── models.py           All data-access functions
├── export.py           Standard Notes export logic
├── seed.py             Sample character data
├── routes/
│   ├── characters.py   Dashboard, character CRUD, query
│   ├── decisions.py    Log and delete story decisions
│   ├── companions.py   Add, edit, delete companions
│   └── export.py       Export endpoints
├── templates/          Jinja2 HTML templates
└── static/             CSS and JS assets
```

## Features

- **Dashboard** — character roster with alignment bars
- **Character sheets** — full detail view with all decisions, companions, and arcs
- **Decision log** — record story choices with alignment impact, context, consequences, companion, and tags
- **Companion tracker** — status, influence level, romance flag, notes
- **Cross-character query** — filter decisions by alignment, companion name, expansion, or character
- **Export** — single character or all characters to Standard Notes format

## Standard Notes Export

### Single character
Click **↓ Export** on the dashboard or character detail page. This downloads a `.json` file for that character.

### All characters
Click **Export All** in the navigation bar. Downloads `swtor-all-characters.json`.

### Importing into Standard Notes

1. Open Standard Notes (desktop app or web at app.standardnotes.com)
2. Go to **Account** (bottom-left) → **Data Backups** → **Import Backup**
3. Select the downloaded `.json` file
4. Each character becomes a Note with structured Markdown content
5. Tags are applied automatically: `swtor`, the class slug (e.g. `jedi-knight`), and the character name slug

**Note:** Standard Notes import works with the unencrypted backup format (version `004`) that this app produces. If you use end-to-end encryption in Standard Notes, you'll need to import while signed in so the app can re-encrypt the notes.

### Export format

Each character note includes:
- Stats (class, species, server)
- Alignment bar (visual text representation)
- Story progress and completed arcs
- Full decision log with context and consequences
- Companions table
- Freeform notes

## Database Location

`C:\Users\<you>\swtor-tracker\swtor.db`

To back up your data, copy this file. To move to another machine, copy the file and place it at the same path.

## Environment Variable

Set `SECRET_KEY` for a production-grade session secret:

```bash
set SECRET_KEY=your-secret-here   # Windows
python app.py
```
