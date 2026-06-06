from common import get_conn, out_bool, out_table


def insert_admin(uid, email, username, joined, firstname, lastname):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO User (uid, email, username, joined) VALUES (%s, %s, %s, %s)",(uid, email, username, joined))
        cur.execute("INSERT INTO Administrator (uid, firstname, lastname) VALUES (%s, %s, %s)",(uid, firstname, lastname))
        conn.commit()
        out_bool(True)
    except Exception:
        if conn:
            conn.rollback()
        out_bool(False)
    finally:
        if conn:
            conn.close()


def add_venue(eid, vid, is_primary):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        if is_primary == 1:
            cur.execute("SELECT 1 FROM Hosting WHERE eid = %s AND is_primary = 1", (eid,))
            if cur.fetchone():
                out_bool(False)
                return
        cur.execute("INSERT INTO Hosting (eid, vid, is_primary) VALUES (%s, %s, %s)",(eid, vid, is_primary))
        conn.commit()
        out_bool(True)
    except Exception:
        if conn:
            conn.rollback()
        out_bool(False)
    finally:
        if conn:
            conn.close()


def venue_events(vid):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.eid, e.title, e.type, e.datetime, h.is_primary
            FROM Hosting h
            JOIN Event e ON e.eid = h.eid
            WHERE h.vid = %s
            ORDER BY e.datetime ASC, e.eid ASC
        """, (vid,))
        out_table(cur.fetchall())
    finally:
        if conn:
            conn.close()
