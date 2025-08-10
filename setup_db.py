import sqlite3
import json

# Define the database file name and the questions file
DB_FILE = 'database.db'
QUESTIONS_FILE = 'questions.json'

def setup_database():
    """Connects to the database and creates the questions table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            question_text TEXT NOT NULL,
            question_image TEXT,
            options_json TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' and 'questions' table created.")

def populate_questions():
    """Loads questions from the JSON file and inserts them into the database."""
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{QUESTIONS_FILE}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode '{QUESTIONS_FILE}'. Check the JSON format.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for q in questions:
        question_id = q.get('id')
        question_type = q.get('type')
        question_text = q.get('question_text')
        question_image = q.get('question_image')
        options_json = json.dumps(q.get('options'))

        cursor.execute('''
            INSERT OR REPLACE INTO questions (id, type, question_text, question_image, options_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (question_id, question_type, question_text, question_image, options_json))

    conn.commit()
    conn.close()
    print(f"Successfully loaded {len(questions)} questions into the database.")

if __name__ == '__main__':
    setup_database()
    populate_questions()