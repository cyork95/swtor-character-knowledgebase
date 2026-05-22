import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from db import get_db


def seed():
    app = create_app()
    with app.app_context():
        db = get_db()

        count = db.execute('SELECT COUNT(*) FROM characters').fetchone()[0]
        if count > 0:
            print(f'Database already has {count} character(s). Skipping seed.')
            print('Delete ~/swtor-tracker/swtor.db and re-run to reset.')
            return

        # ------------------------------------------------------------------
        # Character 1: Aria Solaris — Jedi Knight / Guardian
        # ------------------------------------------------------------------
        c = db.execute(
            '''INSERT INTO characters
               (name, class, advanced_class, species, server,
                light_side_pts, dark_side_pts, current_chapter, current_expansion, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            ('Aria Solaris', 'Jedi Knight', 'Guardian', 'Human', 'Star Forge',
             2450, 800, 'Chapter 3', 'Knights of the Fallen Empire',
             'Main story character. Completed the Ziost arc before KotFE.')
        )
        aria_id = c.lastrowid

        # Aria's decisions
        d1 = db.execute(
            '''INSERT INTO story_decisions
               (character_id, choice, context, consequence,
                alignment_impact, alignment_points, companion_involved)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (aria_id,
             'Spared the captured Sith prisoner on Tython',
             'Tython, early class story — prisoner begged for mercy',
             'Prisoner later aided the Republic cause as an informant',
             'LIGHT', 150, 'T7-O1')
        ).lastrowid
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d1, 'mercy'))
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d1, 'class-story'))

        d2 = db.execute(
            '''INSERT INTO story_decisions
               (character_id, choice, context, consequence,
                alignment_impact, alignment_points, companion_involved)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (aria_id,
             'Helped the Corellian refugees despite orders to retreat',
             'Corellia — civilian crisis during SIS operation',
             'Saved 200 civilians; earned a public commendation from the Senate',
             'LIGHT', 100, 'Kira Carsen')
        ).lastrowid
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d2, 'sacrifice'))
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d2, 'corellia'))

        d3 = db.execute(
            '''INSERT INTO story_decisions
               (character_id, choice, context, consequence,
                alignment_impact, alignment_points, companion_involved)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (aria_id,
             'Executed the crime lord rather than turning him over to Republic custody',
             'Nar Shaddaa — Hutt Cartel expansion',
             'Sent a message to the underworld; Kira disapproved',
             'DARK', 200, 'Kira Carsen')
        ).lastrowid
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d3, 'dark-side'))
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d3, 'hutt-cartel'))

        # Aria's companions
        db.executemany(
            '''INSERT INTO companions
               (character_id, name, status, relationship_level, is_romance, notable_interactions)
               VALUES (?, ?, ?, ?, ?, ?)''',
            [
                (aria_id, 'T7-O1', 'active', 30, 0,
                 'Original astromech partner from Tython. Loyal above all others.'),
                (aria_id, 'Kira Carsen', 'romance', 45, 1,
                 'Former Children of the Emperor. Romance route. Disappeared during KotFE.'),
                (aria_id, 'Doc', 'inactive', 20, 0,
                 'Field medic. Relationship strained after Nar Shaddaa decision.'),
                (aria_id, 'Lord Scourge', 'active', 35, 0,
                 'Former Sith Emperor\'s Wrath. Unlikely but steadfast ally.'),
            ]
        )

        # Aria's story arcs
        db.executemany(
            'INSERT INTO story_arcs (character_id, arc_name, expansion) VALUES (?, ?, ?)',
            [
                (aria_id, 'Jedi Knight Class Story', 'Base Game'),
                (aria_id, 'Rise of the Hutt Cartel', 'Rise of the Hutt Cartel'),
                (aria_id, 'Shadow of Revan', 'Shadow of Revan'),
            ]
        )

        db.commit()
        print(f'  Created Aria Solaris (id={aria_id})')

        # ------------------------------------------------------------------
        # Character 2: Darth Vexus — Sith Inquisitor / Sorcerer
        # ------------------------------------------------------------------
        c = db.execute(
            '''INSERT INTO characters
               (name, class, advanced_class, species, server,
                light_side_pts, dark_side_pts, current_chapter, current_expansion, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            ('Darth Vexus', 'Sith Inquisitor', 'Sorcerer', 'Zabrak', 'Darth Malgus',
             200, 4200, 'Chapter 2', 'Knights of the Eternal Throne',
             'Pure dark side run. Bound all four Force ghosts. Highest DS ranking achievable.')
        )
        vexus_id = c.lastrowid

        # Vexus's decisions
        d4 = db.execute(
            '''INSERT INTO story_decisions
               (character_id, choice, context, consequence,
                alignment_impact, alignment_points, companion_involved)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (vexus_id,
             'Destroyed the ancient Sith library to prevent rivals from accessing it',
             'Dromund Kaas — early Inquisitor class story',
             'Gained immense power but earned the enmity of the Dark Council historians',
             'DARK', 300, 'Khem Val')
        ).lastrowid
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d4, 'power'))
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d4, 'class-story'))

        d5 = db.execute(
            '''INSERT INTO story_decisions
               (character_id, choice, context, consequence,
                alignment_impact, alignment_points, companion_involved)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (vexus_id,
             'Sacrificed the Hutt informant to fuel a Sith ritual',
             'Nar Shaddaa — Hutt Cartel expansion',
             'Ritual succeeded; informant\'s force-imprint bound as a servant',
             'DARK', 250, 'Ashara Zavros')
        ).lastrowid
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d5, 'ritual'))
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d5, 'hutt-cartel'))

        d6 = db.execute(
            '''INSERT INTO story_decisions
               (character_id, choice, context, consequence,
                alignment_impact, alignment_points, companion_involved)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (vexus_id,
             'Usurped Darth Thanaton\'s seat on the Dark Council through force and treachery',
             'Dark Council chambers — end of Inquisitor class story',
             'Became Darth Nox; secured permanent seat on the Dark Council',
             'DARK', 400, 'Khem Val')
        ).lastrowid
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d6, 'dark-council'))
        db.execute('INSERT INTO choice_tags (decision_id, tag) VALUES (?, ?)',
                   (d6, 'class-story'))

        # Vexus's companions
        db.executemany(
            '''INSERT INTO companions
               (character_id, name, status, relationship_level, is_romance, notable_interactions)
               VALUES (?, ?, ?, ?, ?, ?)''',
            [
                (vexus_id, 'Khem Val', 'active', 40, 0,
                 'Ancient Dashade bound to the Inquisitor. Shares body with Darth Zash.'),
                (vexus_id, 'Ashara Zavros', 'inactive', 25, 0,
                 'Togruta Jedi Padawan turned Sith apprentice. Conflicts with dark side choices.'),
                (vexus_id, 'Talos Drellik', 'active', 30, 0,
                 'Sith Intelligence field researcher. Enthusiastic about Sith artifacts.'),
            ]
        )

        # Vexus's story arcs
        db.executemany(
            'INSERT INTO story_arcs (character_id, arc_name, expansion) VALUES (?, ?, ?)',
            [
                (vexus_id, 'Sith Inquisitor Class Story', 'Base Game'),
                (vexus_id, 'Rise of the Hutt Cartel', 'Rise of the Hutt Cartel'),
            ]
        )

        db.commit()
        print(f'  Created Darth Vexus (id={vexus_id})')
        print('Seed complete. Visit http://127.0.0.1:5000 after starting the app.')


if __name__ == '__main__':
    seed()
