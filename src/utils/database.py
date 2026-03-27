import sqlite3
import os
import datetime

DB_PATH = "leads.db"

def _get_connection():
    """Helper function to get a database connection."""
    # check_same_thread=False is often needed for multi-threaded apps like Streamlit
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initialize the database and create the leads table if it doesn't exist."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            company_name TEXT,
            company_url TEXT,
            summary TEXT,
            pain_points TEXT,
            email_draft TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_lead(company_name, company_url, summary, pain_points, email_draft, score):
    """Insert a new lead record into the database."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Generate local timestamp in Python to avoid UTC issues in SQLite
    local_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    cursor.execute('''
        INSERT INTO leads (company_name, company_url, summary, pain_points, email_draft, score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (company_name, company_url, summary, pain_points, email_draft, score, local_time))
    
    conn.commit()
    conn.close()

def get_all_leads():
    """Fetch all lead records ordered by created_at DESC."""
    conn = _get_connection()
    conn.row_factory = sqlite3.Row  # To return dictionary-like objects
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
    rows = cursor.fetchall()
    
    conn.close()
    
    return [dict(row) for row in rows]
