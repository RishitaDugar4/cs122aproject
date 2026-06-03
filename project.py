import mysql.connector
import sys
import os
import csv

def open_connection():
    '''Open connection to database cs122a using the provided autograder credentials'''
    return mysql.connector.connect(
        user='test', 
        password='password', 
        database='cs122a'
    )

import sys
import os
import csv
import mysql.connector


# CREATE TABLE statements. Order matters for creation (parents before children)
DDL_STATEMENTS = [
    """
    CREATE TABLE User (
    uid INT,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    joined DATE NOT NULL,
    PRIMARY KEY (uid)
    )
    """,
    """
    CREATE TABLE Administrator (
    uid INT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Organizer (
    uid INT,
    department TEXT NOT NULL,
    experience INT NOT NULL,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Participant (
    uid INT,
    type TEXT,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Event (
    eid INT,
    creator_uid INT NOT NULL,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    PRIMARY KEY (eid),
    FOREIGN KEY (creator_uid) REFERENCES Organizer(uid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Slot (
    eid INT,
    snum INT NOT NULL,
    is_reserved BOOLEAN NOT NULL,
    uid INT,
    PRIMARY KEY (eid, snum),
    FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
    FOREIGN KEY (uid) REFERENCES Participant(uid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Venue (
    vid INT,
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL,
    PRIMARY KEY (vid)
    )
    """,
    """
    CREATE TABLE OnCampus (
    vid INT,
    code TEXT NOT NULL,
    PRIMARY KEY (vid),
    FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE OffCampus (
    vid INT,
    distance INT NOT NULL,
    PRIMARY KEY (vid),
    FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Hosting (
    eid INT NOT NULL,
    vid INT NOT NULL,
    is_primary BOOLEAN NOT NULL,
    PRIMARY KEY (eid, vid),
    FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
    FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE Approval (
    uid INT NOT NULL,
    vid INT NOT NULL,
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    PRIMARY KEY (uid, vid),
    FOREIGN KEY (uid) REFERENCES Administrator(uid) ON DELETE CASCADE,
    FOREIGN KEY (vid) REFERENCES OffCampus(vid) ON DELETE CASCADE
    )
    """,
]

# Tables in dependency order (parents first). Used for dropping (reversed) and loading.
TABLE_ORDER = [
    "User",
    "Administrator",
    "Organizer",
    "Participant",
    "Venue",
    "OnCampus",
    "OffCampus",
    "Event",
    "Slot",
    "Hosting",
    "Approval",
]

# Maps each table to the CSV filename and the number of columns it has.
TABLE_FILES = {
    "User": ("User.csv", 4),
    "Administrator": ("Administrator.csv", 3),
    "Organizer": ("Organizer.csv", 3),
    "Participant": ("Participant.csv", 2),
    "Venue": ("Venue.csv", 5),
    "OnCampus": ("OnCampus.csv", 2),
    "OffCampus": ("OffCampus.csv", 2),
    "Event": ("Event.csv", 5),
    "Slot": ("Slot.csv", 4),
    "Hosting": ("Hosting.csv", 3),
    "Approval": ("Approval.csv", 4),
}


def import_data(folder_name):
    """Drop all tables, recreate them, and load every CSV from the given folder."""
    conn = open_connection()
    cursor = conn.cursor()
    try:
        # Disable FK checks (allows order-independent dropping/loading)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for table in reversed(TABLE_ORDER):
            cursor.execute(f"DROP TABLE IF EXISTS {table}")

        for ddl in DDL_STATEMENTS:
            cursor.execute(ddl)

        for table in TABLE_ORDER:
            filename, num_cols = TABLE_FILES[table]
            path = os.path.join(folder_name, filename)
            rows = []
            with open(path, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    # Convert the literal "NULL" into a None
                    cleaned = [None if v == "NULL" else v for v in row]
                    rows.append(cleaned)
            if rows:
                placeholders = ", ".join(["%s"] * num_cols)
                cursor.executemany(
                    f"INSERT INTO {table} VALUES ({placeholders})", rows
                )

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("Success")
    except Exception:
        conn.rollback()
        print("Fail")
    finally:
        cursor.close()
        conn.close()


def insert_admin(uid, email, username, joined, firstname, lastname):
    """Insert a new user and the matching administrator row."""
    conn = open_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO User (uid, email, username, joined) VALUES (%s, %s, %s, %s)",
            (uid, email, username, joined),
        )
        cursor.execute(
            "INSERT INTO Administrator (uid, firstname, lastname) VALUES (%s, %s, %s)",
            (uid, firstname, lastname),
        )
        conn.commit()
        print("Success")
    except Exception:
        conn.rollback()
        print("Fail")
    finally:
        cursor.close()
        conn.close()


def add_venue(eid, vid, is_primary):
    """Add a venue to an event via Hosting, enforcing a single primary venue per event."""
    conn = open_connection()
    cursor = conn.cursor()
    try:
        if is_primary:
            cursor.execute(
                "SELECT COUNT(*) FROM Hosting WHERE eid = %s AND is_primary = TRUE",
                (eid,),
            )
            if cursor.fetchone()[0] > 0:
                print("Fail")
                return

        cursor.execute(
            "INSERT INTO Hosting (eid, vid, is_primary) VALUES (%s, %s, %s)",
            (eid, vid, is_primary),
        )
        conn.commit()
        print("Success")
    except Exception:
        conn.rollback()
        print("Fail")
    finally:
        cursor.close()
        conn.close()


def parse_bool(value):
    """Parse a command-line boolean like 'true'/'false' into a Python bool."""
    return str(value).strip().lower() in ("true", "1", "yes", "t")


def main():
    args = sys.argv
    func = args[1]

    if func == "import":
        import_data(args[2])
    elif func == "insertAdmin":
        insert_admin(args[2], args[3], args[4], args[5], args[6], args[7])
    elif func == "addVenue":
        add_venue(int(args[2]), int(args[3]), parse_bool(args[4]))


if __name__ == "__main__":
    main()
