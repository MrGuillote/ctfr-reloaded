import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ScanHistory:
    def __init__(self, db_path, enabled=True):
        self.enabled = enabled
        self.db_path = Path(db_path)
        if self.enabled:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()

    def _connect(self):
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    scanned_at TEXT NOT NULL,
                    count INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subdomains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT,
                    FOREIGN KEY (scan_id) REFERENCES scans(id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_subdomains_scan ON subdomains(scan_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_subdomains_name ON subdomains(name)"
            )

    def save_scan(self, domain, items):
        if not self.enabled:
            return None
        import json

        scanned_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO scans (domain, scanned_at, count) VALUES (?, ?, ?)",
                (domain, scanned_at, len(items)),
            )
            scan_id = cursor.lastrowid
            for item in items:
                conn.execute(
                    "INSERT INTO subdomains (scan_id, name, data) VALUES (?, ?, ?)",
                    (scan_id, item["name"], json.dumps(item, ensure_ascii=False)),
                )
            conn.commit()
        return scan_id

    def get_last_names(self, domain):
        if not self.enabled:
            return set()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id FROM scans
                WHERE domain = ?
                ORDER BY id DESC LIMIT 1
                """,
                (domain,),
            ).fetchone()
            if not row:
                return set()
            scan_id = row[0]
            rows = conn.execute(
                "SELECT name FROM subdomains WHERE scan_id = ?",
                (scan_id,),
            ).fetchall()
        return {r[0].lower() for r in rows}

    def get_new_since_last(self, domain, current_names):
        previous = self.get_last_names(domain)
        return sorted(name for name in current_names if name.lower() not in previous)
