# database.py
import sqlite3
import os

DB_PATH = "portfolio.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        # Portfolio projects table
        db.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                link TEXT NOT NULL
            )
        ''')
        cur = db.execute('SELECT COUNT(*) FROM portfolio_projects')
        if cur.fetchone()[0] == 0:
            default_projects = [
                ("Crypto Alert Bot", "Real-time cryptocurrency price alerts with custom thresholds, multi‑exchange support, and instant push notifications.", "https://t.me/YourDemoBot"),
                ("Task Manager Mini App", "Team productivity tool with task assignment, deadline tracking, file attachments, and real‑time sync.", "https://t.me/YourDemoApp"),
                ("E‑commerce Website", "Full‑featured online store with payment integration, inventory management, and admin dashboard.", "https://yourdemo.com"),
                ("Social Media Automation", "Auto‑post across platforms (Twitter, Telegram, Discord) with scheduling, content recycling, and analytics.", "https://t.me/YourDemoBot")
            ]
            db.executemany('INSERT INTO portfolio_projects (name, description, link) VALUES (?, ?, ?)', default_projects)

        # Users table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

# ---------- Portfolio functions ----------
def get_portfolio_projects():
    with get_db() as db:
        cur = db.execute('SELECT * FROM portfolio_projects ORDER BY id')
        return cur.fetchall()

def add_portfolio_project(name, description, link):
    with get_db() as db:
        cur = db.execute('INSERT INTO portfolio_projects (name, description, link) VALUES (?, ?, ?)',
                         (name, description, link))
        return cur.lastrowid

def update_portfolio_project(project_id, name, description, link):
    with get_db() as db:
        db.execute('UPDATE portfolio_projects SET name = ?, description = ?, link = ? WHERE id = ?',
                   (name, description, link, project_id))

def delete_portfolio_project(project_id):
    with get_db() as db:
        db.execute('DELETE FROM portfolio_projects WHERE id = ?', (project_id,))

def get_portfolio_project(project_id):
    with get_db() as db:
        cur = db.execute('SELECT * FROM portfolio_projects WHERE id = ?', (project_id,))
        return cur.fetchone()

# ---------- User functions ----------
def register_user(user_id, username, first_name, last_name):
    with get_db() as db:
        db.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))

def get_all_users():
    with get_db() as db:
        cur = db.execute('SELECT * FROM users ORDER BY joined_date DESC')
        return cur.fetchall()

def get_user_count():
    with get_db() as db:
        cur = db.execute('SELECT COUNT(*) as count FROM users')
        return cur.fetchone()['count']