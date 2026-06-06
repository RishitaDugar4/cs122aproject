from common import get_conn, out_bool, out_table


def reserve_slot(eid, snum, uid):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE Slot SET is_reserved = 1, uid = %s WHERE eid = %s AND snum = %s AND is_reserved = 0",(uid, eid, snum))
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


def cancel_reservation(eid, snum, uid):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE Slot SET is_reserved = 0, uid = NULL WHERE eid = %s AND snum = %s AND uid = %s AND is_reserved = 1",(eid, snum, uid))
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


def participant_schedule(uid):
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.eid, e.title, e.type, e.datetime, s.snum, v.vid, v.street, v.city, v.state, v.zip
            FROM Slot s
            JOIN Event e ON s.eid = e.eid
            LEFT JOIN Hosting h ON h.eid = e.eid AND h.is_primary = 1
            LEFT JOIN Venue v ON v.vid = h.vid
            WHERE s.uid = %s AND s.is_reserved = 1
            ORDER BY e.datetime ASC
        """, (uid,))
        out_table(cur.fetchall())
    finally:
        if conn:
            conn.close()
