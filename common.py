import mysql.connector

def get_conn():
    return mysql.connector.connect(user='test',password='password',database='cs122a')

def out_bool(ok):
    print("Success" if ok else "Fail")

def out_table(rows):
    for r in rows:
        print(",".join("NULL" if v is None else str(v) for v in r))

def to_none(v):
    return None if v == "NULL" else v

def to_bool(v):
    return 1 if str(v).lower() == "true" else 0

TABLES = [
    ("User", """
        CREATE TABLE User (
            uid INT,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            joined DATE NOT NULL,
            PRIMARY KEY (uid))"""),
    ("Organizer", """
        CREATE TABLE Organizer (
            uid INT,
            department TEXT NOT NULL,
            experience INT NOT NULL,
            PRIMARY KEY (uid),
            FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE)"""),
    ("Participant", """
        CREATE TABLE Participant (
            uid INT,
            type TEXT,
            PRIMARY KEY (uid),
            FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE)"""),
    ("Administrator", """
        CREATE TABLE Administrator (
            uid INT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            PRIMARY KEY (uid),
            FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE)"""),
    ("Event", """
        CREATE TABLE Event (
            eid INT,
            creator_uid INT NOT NULL,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            datetime DATETIME NOT NULL,
            PRIMARY KEY (eid),
            FOREIGN KEY (creator_uid) REFERENCES Organizer(uid) ON DELETE CASCADE)"""),
    ("Slot", """
        CREATE TABLE Slot (
            eid INT,
            snum INT NOT NULL,
            is_reserved BOOLEAN NOT NULL,
            uid INT,
            PRIMARY KEY (eid, snum),
            FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
            FOREIGN KEY (uid) REFERENCES Participant(uid) ON DELETE CASCADE)"""),
    ("Venue", """
        CREATE TABLE Venue (
            vid INT,
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip TEXT NOT NULL,
            PRIMARY KEY (vid))"""),
    ("OnCampus", """
        CREATE TABLE OnCampus (
            vid INT,
            code TEXT NOT NULL,
            PRIMARY KEY (vid),
            FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE)"""),
    ("OffCampus", """
        CREATE TABLE OffCampus (
            vid INT,
            distance INT NOT NULL,
            PRIMARY KEY (vid),
            FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE)"""),
    ("Hosting", """
        CREATE TABLE Hosting (
            eid INT NOT NULL,
            vid INT NOT NULL,
            is_primary BOOLEAN NOT NULL,
            PRIMARY KEY (eid, vid),
            FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
            FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE)"""),
    ("Approval", """
        CREATE TABLE Approval (
            uid INT NOT NULL,
            vid INT NOT NULL,
            valid_from DATE NOT NULL,
            valid_until DATE NOT NULL,
            PRIMARY KEY (uid, vid),
            FOREIGN KEY (uid) REFERENCES Administrator(uid) ON DELETE CASCADE,
            FOREIGN KEY (vid) REFERENCES OffCampus(vid) ON DELETE CASCADE)""")]

COLUMNS = {
    "User": ["uid", "email", "username", "joined"],
    "Organizer": ["uid", "department", "experience"],
    "Participant": ["uid", "type"],
    "Administrator": ["uid", "firstname", "lastname"],
    "Event": ["eid", "creator_uid", "title", "type", "datetime"],
    "Slot": ["eid", "snum", "is_reserved", "uid"],
    "Venue": ["vid", "street", "city", "state", "zip"],
    "OnCampus": ["vid", "code"],
    "OffCampus": ["vid", "distance"],
    "Hosting": ["eid", "vid", "is_primary"],
    "Approval": ["uid", "vid", "valid_from", "valid_until"],
}
