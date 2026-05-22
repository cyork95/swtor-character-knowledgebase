import sqlite3
from pathlib import Path
from flask import g

DB_PATH = Path.home() / 'swtor-tracker' / 'swtor.db'

_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class TEXT,
    advanced_class TEXT,
    species TEXT,
    server TEXT,
    light_side_pts INTEGER DEFAULT 0,
    dark_side_pts INTEGER DEFAULT 0,
    current_chapter TEXT,
    current_expansion TEXT,
    legacy TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS story_arcs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    arc_name TEXT,
    expansion TEXT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS story_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    choice TEXT NOT NULL,
    context TEXT,
    consequence TEXT,
    alignment_impact TEXT CHECK(alignment_impact IN ('LIGHT', 'DARK', 'NEUTRAL')),
    alignment_points INTEGER DEFAULT 0,
    companion_involved TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS companions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active'
        CHECK(status IN ('active', 'inactive', 'dead', 'romance', 'exiled')),
    relationship_level INTEGER DEFAULT 0,
    is_romance BOOLEAN DEFAULT 0,
    notable_interactions TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS choice_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER NOT NULL,
    tag TEXT,
    FOREIGN KEY (decision_id) REFERENCES story_decisions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS influence_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    companion_name TEXT NOT NULL,
    influence_change INTEGER NOT NULL,
    source TEXT,
    notes TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS session_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    session_date TEXT,
    summary TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_outfits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    outfit_name TEXT NOT NULL DEFAULT 'Outfit 1',
    slot_number INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 0,
    head TEXT,
    chest TEXT,
    legs TEXT,
    hands TEXT,
    feet TEXT,
    waist TEXT,
    wrists TEXT,
    main_hand TEXT,
    off_hand TEXT,
    dye_module TEXT,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS companion_outfits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    companion_name TEXT NOT NULL,
    outfit_name TEXT DEFAULT 'Default',
    head TEXT,
    chest TEXT,
    legs TEXT,
    hands TEXT,
    feet TEXT,
    waist TEXT,
    wrists TEXT,
    main_hand TEXT,
    off_hand TEXT,
    dye_module TEXT,
    notes TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS planet_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    planet_name TEXT NOT NULL,
    status TEXT DEFAULT 'in_progress'
        CHECK(status IN ('not_started', 'in_progress', 'complete')),
    bonus_series INTEGER DEFAULT 0,
    datacrons INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS character_titles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    earned_at TEXT,
    notes TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
);

CREATE TRIGGER IF NOT EXISTS trg_characters_updated_at
    AFTER UPDATE ON characters FOR EACH ROW
    BEGIN UPDATE characters SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;

CREATE TRIGGER IF NOT EXISTS trg_companions_updated_at
    AFTER UPDATE ON companions FOR EACH ROW
    BEGIN UPDATE companions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;
"""


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(_SCHEMA)
    conn.commit()
    conn.close()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
