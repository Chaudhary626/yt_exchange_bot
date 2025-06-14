import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                last_active TIMESTAMP
            );
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                thumbnail TEXT,
                duration INTEGER,
                link TEXT,
                actions TEXT,
                method TEXT,
                instructions TEXT,
                status TEXT,
                assigned_to INTEGER,
                proof TEXT,
                verified_by_owner INTEGER DEFAULT 0,
                created_at TIMESTAMP
            );
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                reported_by INTEGER,
                reason TEXT,
                created_at TIMESTAMP
            );
        ''')
        db.commit()

# ---- User Operations ----
def get_or_create_user(user_id, username):
    with get_db() as db:
        res = db.execute('SELECT * FROM users WHERE user_id=?', (user_id,)).fetchone()
        if not res:
            db.execute('INSERT INTO users (user_id, username, last_active) VALUES (?, ?, ?)', (user_id, username, datetime.utcnow()))
            db.commit()
            return True
        else:
            db.execute('UPDATE users SET last_active=? WHERE user_id=?', (datetime.utcnow(), user_id))
            db.commit()
            return False

def update_last_active(user_id):
    with get_db() as db:
        db.execute('UPDATE users SET last_active=? WHERE user_id=?', (datetime.utcnow(), user_id))
        db.commit()

def get_user_video_count(user_id):
    with get_db() as db:
        res = db.execute("SELECT COUNT(*) FROM videos WHERE user_id=? AND status!='removed'", (user_id,)).fetchone()
        return res[0] if res else 0

def get_user_videos(user_id):
    with get_db() as db:
        res = db.execute("SELECT * FROM videos WHERE user_id=? AND status!='removed' ORDER BY created_at DESC", (user_id,))
        return res.fetchall()

def remove_video(video_id, user_id):
    with get_db() as db:
        db.execute("UPDATE videos SET status='removed' WHERE id=? AND user_id=?", (video_id, user_id))
        db.commit()

# ---- Video Operations ----
def submit_video(user_id, title, thumbnail, duration, link, actions, method, instructions):
    with get_db() as db:
        db.execute('''
            INSERT INTO videos
            (user_id, title, thumbnail, duration, link, actions, method, instructions, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        ''', (user_id, title, thumbnail, duration, link, actions, method, instructions, datetime.utcnow()))
        db.commit()

def get_pending_videos_to_assign(current_user_id):
    with get_db() as db:
        # Not submitted by self, not already assigned, not completed/removed
        res = db.execute('''
            SELECT * FROM videos
            WHERE user_id!=? AND status='pending' AND (assigned_to IS NULL OR assigned_to=0)
            ORDER BY created_at ASC
        ''', (current_user_id,))
        return res.fetchall()

def assign_video_to_user(video_id, user_id):
    with get_db() as db:
        db.execute('UPDATE videos SET assigned_to=?, status="assigned" WHERE id=?', (user_id, video_id))
        db.commit()

def get_assigned_video_for_user(user_id):
    with get_db() as db:
        res = db.execute('''
            SELECT * FROM videos WHERE assigned_to=? AND status='assigned'
        ''', (user_id,))
        return res.fetchone()

def set_video_proof(video_id, proof):
    with get_db() as db:
        db.execute('UPDATE videos SET proof=?, status="proof_submitted" WHERE id=?', (proof, video_id))
        db.commit()

def get_videos_with_proof_for_owner(owner_id):
    with get_db() as db:
        res = db.execute('''
            SELECT * FROM videos WHERE user_id=? AND proof IS NOT NULL AND status="proof_submitted"
        ''', (owner_id,))
        return res.fetchall()

def approve_proof(video_id):
    with get_db() as db:
        db.execute('UPDATE videos SET verified_by_owner=1, status="completed" WHERE id=?', (video_id,))
        db.commit()

def reject_proof(video_id):
    with get_db() as db:
        db.execute('UPDATE videos SET proof=NULL, status="assigned" WHERE id=?', (video_id,))
        db.commit()

def unassign_expired_tasks():
    # Unassign assigned videos if 15 minutes passed since assigned
    with get_db() as db:
        expired = db.execute('''
            SELECT id, assigned_to FROM videos
            WHERE status="assigned" AND assigned_to IS NOT NULL AND assigned_to>0
            AND DATETIME(created_at, '+15 minutes') < DATETIME('now')
        ''').fetchall()
        for row in expired:
            db.execute('UPDATE videos SET assigned_to=NULL, status="pending" WHERE id=?', (row['id'],))
            block_user_from_new_tasks(row['assigned_to'])
        db.commit()

def block_user_from_new_tasks(user_id):
    with get_db() as db:
        # Add a flag table/column if you want, or simply set a timeout field in users
        db.execute('UPDATE users SET last_active=? WHERE user_id=?', (datetime.utcnow() - timedelta(hours=1), user_id))
        db.commit()

def unblock_user(user_id):
    update_last_active(user_id)

def user_is_blocked(user_id):
    with get_db() as db:
        res = db.execute('SELECT last_active FROM users WHERE user_id=?', (user_id,)).fetchone()
        if not res:
            return True
        # If last_active is more than 10 minutes ago, blocked
        last_active = datetime.strptime(res['last_active'], '%Y-%m-%d %H:%M:%S.%f')
        return (datetime.utcnow() - last_active) > timedelta(minutes=20)

def get_video_by_id(video_id):
    with get_db() as db:
        return db.execute('SELECT * FROM videos WHERE id=?', (video_id,)).fetchone()

def get_owner_id_by_video(video_id):
    with get_db() as db:
        res = db.execute('SELECT user_id FROM videos WHERE id=?', (video_id,)).fetchone()
        return res['user_id'] if res else None

# ---- Reports ----
def add_report(video_id, reported_by, reason):
    with get_db() as db:
        db.execute('''
            INSERT INTO reports (video_id, reported_by, reason, created_at)
            VALUES (?, ?, ?, ?)
        ''', (video_id, reported_by, reason, datetime.utcnow()))
        db.commit()

def get_reports():
    with get_db() as db:
        res = db.execute('SELECT * FROM reports').fetchall()
        return res

# ---- Initialization ----
init_db()