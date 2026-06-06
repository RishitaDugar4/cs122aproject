from common import get_conn, out_table


def available_events(date):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.eid, e.title, e.type, e.datetime, COUNT(s.snum)
            FROM Event e JOIN Slot s ON e.eid = s.eid
            WHERE s.is_reserved = 0 AND e.datetime >= %s
            GROUP BY e.eid, e.title, e.type, e.datetime
            ORDER BY e.datetime ASC, e.eid ASC
        """, (date,))
        out_table(cur.fetchall())
    finally:
        if conn:
            conn.close()


def popular_event_types(n):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.type, COUNT(*)
            FROM Event e JOIN Slot s ON e.eid = s.eid
            WHERE s.is_reserved = 1
            GROUP BY e.type
            HAVING COUNT(*) >= %s
            ORDER BY COUNT(*) DESC, e.type ASC
        """, (n,))
        out_table(cur.fetchall())
    finally:
        if conn:
            conn.close()


def organizer_stats(n):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.uid, u.username, o.department, COUNT(ev.eid)
            FROM Organizer o
            JOIN User u ON u.uid = o.uid
            JOIN Event ev ON ev.creator_uid = o.uid
            GROUP BY o.uid, u.username, o.department
            HAVING COUNT(ev.eid) >= %s
            ORDER BY COUNT(ev.eid) DESC, o.uid ASC
        """, (n,))
        out_table(cur.fetchall())
    finally:
        if conn:
            conn.close()
