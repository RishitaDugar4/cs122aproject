import os
import csv
from common import get_conn, out_bool, TABLES, COLUMNS


def do_import(folder):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        for name, _ in reversed(TABLES):
            cur.execute("DROP TABLE IF EXISTS " + name)
        for _, ddl in TABLES:
            cur.execute(ddl)
        for name, _ in TABLES:
            cols = COLUMNS[name]
            path = os.path.join(folder, name + ".csv")
            placeholders = ",".join(["%s"] * len(cols))
            sql = "INSERT INTO " + name + " (" + ",".join(cols) + ") VALUES (" + placeholders + ")"
            rows = []
            with open(path, newline="", encoding="utf-8") as f:
                for line in csv.reader(f):
                    if not line:
                        continue
                    rows.append([None if x == "NULL" else x for x in line])
            if rows:
                cur.executemany(sql, rows)
        conn.commit()
        out_bool(True)
    except Exception:
        if conn:
            conn.rollback()
        out_bool(False)
    finally:
        if conn:
            conn.close()


def update_event(eid, title, dt):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM Event WHERE eid = %s", (eid,))
        if not cur.fetchone():
            out_bool(False)
            return
        cur.execute("UPDATE Event SET title = %s, datetime = %s WHERE eid = %s",(title, dt, eid))
        conn.commit()
        out_bool(True)
    except Exception:
        if conn:
            conn.rollback()
        out_bool(False)
    finally:
        if conn:
            conn.close()


def delete_organizer(uid):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM Organizer WHERE uid = %s", (uid,))
        if cur.rowcount > 0:
            conn.commit()
            out_bool(True)
        else:
            conn.rollback()
            out_bool(False)
    except Exception:
        if conn:
            conn.rollback()
        out_bool(False)
    finally:
        if conn:
            conn.close()
