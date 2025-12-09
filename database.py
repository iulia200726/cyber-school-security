import sqlite3
import pandas as pd

def create_connection():
    conn = sqlite3.connect('scoala_cyber.db', check_same_thread=False)
    return conn

def create_tables():
    conn = create_connection()
    c = conn.cursor()
    
    # Tabel Tipuri
    c.execute('''CREATE TABLE IF NOT EXISTS tipuri (
        id INTEGER PRIMARY KEY,
        nume TEXT NOT NULL,
        metoda_detectie TEXT,
        risc TEXT NOT NULL
    )''')
    
    # Tabel Incidente
    c.execute('''CREATE TABLE IF NOT EXISTS incidente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_ora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tip_id INTEGER,
        zona TEXT,
        descriere TEXT,
        status TEXT,
        marime_pachet INTEGER,
        FOREIGN KEY (tip_id) REFERENCES tipuri (id)
    )''')
    
    # NOMENCLATOR
    c.execute("SELECT count(*) FROM tipuri")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tipuri VALUES (1, 'SQL Injection', 'Reguli (Regex)', 'Critic')")
        c.execute("INSERT INTO tipuri VALUES (2, 'XSS Attack', 'Reguli (Tags)', 'Ridicat')")
        c.execute("INSERT INTO tipuri VALUES (3, 'HTML Injection', 'Reguli (Tags)', 'Mediu')")
        c.execute("INSERT INTO tipuri VALUES (4, 'Defacement', 'Reguli (CSS)', 'Mediu')")
        c.execute("INSERT INTO tipuri VALUES (5, 'Malware Upload', 'Reguli (Extensie)', 'Critic')")
        c.execute("INSERT INTO tipuri VALUES (6, 'Brute Force', 'Statistica (Loguri)', 'Ridicat')")
        c.execute("INSERT INTO tipuri VALUES (7, 'Port Scanning', 'Statistica (Threshold)', 'Scazut')")
        c.execute("INSERT INTO tipuri VALUES (8, 'Trafic Atipic', 'Machine Learning', 'Critic')")

    conn.commit()
    conn.close()

def add_incident(tip_id, zona, descriere, status, marime_pachet=0):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO incidente (tip_id, zona, descriere, status, marime_pachet) VALUES (?, ?, ?, ?, ?)",
              (tip_id, zona, descriere, status, marime_pachet))
    conn.commit()
    conn.close()

def get_all_incidents():
    conn = create_connection()
    try:
        df = pd.read_sql_query("""
            SELECT i.id, i.data_ora, t.nume as Tip_Atac, t.metoda_detectie, t.risc, i.zona, i.descriere, i.status 
            FROM incidente i
            JOIN tipuri t ON i.tip_id = t.id
            ORDER BY i.data_ora DESC
        """, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

if __name__ == "__main__":
    create_tables()