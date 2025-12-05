import sqlite3
import pandas as pd

def create_connection():
    # check_same_thread=False este CRUCIAL pentru ca Flask si Streamlit sa nu se blocheze reciproc
    conn = sqlite3.connect('scoala_cyber.db', check_same_thread=False)
    return conn

def create_tables():
    conn = create_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS tipuri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nume TEXT NOT NULL,
        risc TEXT NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS incidente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_ora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tip_id INTEGER,
        zona TEXT,
        descriere TEXT,
        status TEXT,
        FOREIGN KEY (tip_id) REFERENCES tipuri (id)
    )''')
    
    # Populare
    c.execute("SELECT count(*) FROM tipuri")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tipuri (id, nume, risc) VALUES (1, 'Phishing/User Suspect', 'Mediu')")
        c.execute("INSERT INTO tipuri (id, nume, risc) VALUES (2, 'SQL Injection', 'Critic')")
        c.execute("INSERT INTO tipuri (id, nume, risc) VALUES (3, 'XSS Scripting', 'Critic')")
        c.execute("INSERT INTO tipuri (id, nume, risc) VALUES (4, 'Malware Upload', 'Critic')")
        c.execute("INSERT INTO tipuri (id, nume, risc) VALUES (5, 'Brute Force', 'Ridicat')")
        c.execute("INSERT INTO tipuri (id, nume, risc) VALUES (6, 'Scanning', 'Mediu')")
    
    conn.commit()
    conn.close()

def add_incident(tip_id, zona, descriere, status):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO incidente (tip_id, zona, descriere, status) VALUES (?, ?, ?, ?)",
              (tip_id, zona, descriere, status))
    conn.commit()
    conn.close()

def get_all_incidents():
    conn = create_connection()
    try:
        df = pd.read_sql_query("""
            SELECT i.id, i.data_ora, t.nume as Tip_Atac, t.risc, i.zona, i.descriere, i.status 
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