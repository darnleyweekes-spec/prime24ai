import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS inquiries (
                id TEXT PRIMARY KEY, scope TEXT NOT NULL, fingerprint TEXT, inquiry TEXT NOT NULL,
                mode TEXT NOT NULL, status TEXT NOT NULL, duplicate_of TEXT REFERENCES inquiries(id),
                created_at TEXT NOT NULL, result_json TEXT, approved_by TEXT, approved_at TEXT);
            CREATE UNIQUE INDEX IF NOT EXISTS active_inquiry ON inquiries(scope, fingerprint)
                WHERE status IN ('processing','pending_approval','approved');
            CREATE TABLE IF NOT EXISTS approval_events (
                id INTEGER PRIMARY KEY, inquiry_id TEXT NOT NULL REFERENCES inquiries(id),
                staff TEXT NOT NULL, at TEXT NOT NULL, from_status TEXT NOT NULL, to_status TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, mode TEXT NOT NULL,
                metadata_json TEXT NOT NULL, summary_json TEXT);
            CREATE TABLE IF NOT EXISTS evaluation_results (
                run_id TEXT NOT NULL REFERENCES evaluation_runs(id), case_id TEXT NOT NULL,
                category TEXT NOT NULL, passed INTEGER NOT NULL, result_json TEXT NOT NULL,
                PRIMARY KEY(run_id, case_id));
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def claim(self, inquiry, scope, fingerprint, mode, status='processing'):
        id = uuid.uuid4().hex
        duplicate_of = None
        with self.connect() as db:
            # Serialize lookup + reservation; prevents concurrent double API calls.
            db.execute('BEGIN IMMEDIATE')
            if status == 'processing':
                old = db.execute("SELECT id FROM inquiries WHERE scope=? AND fingerprint=? AND status IN ('processing','pending_approval','approved')", (scope, fingerprint)).fetchone()
                if old:
                    status, duplicate_of = 'duplicate', old['id']
            db.execute('INSERT INTO inquiries(id,scope,fingerprint,inquiry,mode,status,duplicate_of,created_at) VALUES(?,?,?,?,?,?,?,?)',
                       (id, scope, fingerprint, inquiry, mode, status, duplicate_of, now()))
        return id, duplicate_of

    def finish(self, result):
        with self.connect() as db:
            db.execute('UPDATE inquiries SET status=?,result_json=? WHERE id=?',
                       (result['status'], json.dumps(result), result['id']))

    def approve(self, id, staff, *, confirmed=False):
        if confirmed is not True or not isinstance(staff, str) or not staff.strip() or len(staff.strip()) > 120:
            raise ValueError('Explicit staff confirmation and a staff identifier are required')
        with self.connect() as db:
            at = now()
            updated = db.execute("UPDATE inquiries SET status='approved',approved_by=?,approved_at=? WHERE id=? AND status='pending_approval'",
                                 (staff.strip(), at, id))
            if updated.rowcount != 1:
                raise ValueError('Only a pending draft can be approved once')
            row = db.execute('SELECT result_json FROM inquiries WHERE id=?', (id,)).fetchone()
            result = json.loads(row['result_json'])
            result.update(status='approved', approved_by=staff.strip(), approved_at=at)
            db.execute('UPDATE inquiries SET result_json=? WHERE id=?', (json.dumps(result), id))
            db.execute("INSERT INTO approval_events(inquiry_id,staff,at,from_status,to_status) VALUES(?,?,?,'pending_approval','approved')", (id, staff.strip(), at))

    def get_inquiry(self, id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM inquiries WHERE id=?', (id,)).fetchone()
        return dict(row) if row else None

    def list_inquiries(self, scope='manual:fixture'):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM inquiries WHERE scope=? ORDER BY created_at DESC', (scope,))]

    def start_run(self, mode, metadata):
        id = uuid.uuid4().hex
        with self.connect() as db:
            db.execute('INSERT INTO evaluation_runs(id,started_at,mode,metadata_json) VALUES(?,?,?,?)', (id, now(), mode, json.dumps(metadata)))
        return id

    def save_case(self, run_id, result):
        with self.connect() as db:
            db.execute('INSERT INTO evaluation_results VALUES(?,?,?,?,?)',
                       (run_id, result['case_id'], result['category'], int(result['passed']), json.dumps(result)))

    def finish_run(self, id, summary):
        with self.connect() as db:
            db.execute('UPDATE evaluation_runs SET finished_at=?,summary_json=? WHERE id=?', (now(), json.dumps(summary), id))

    def runs(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM evaluation_runs ORDER BY started_at DESC')]

    def results(self, id):
        with self.connect() as db:
            return [json.loads(r['result_json']) for r in db.execute('SELECT result_json FROM evaluation_results WHERE run_id=? ORDER BY case_id', (id,))]
