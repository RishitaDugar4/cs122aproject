==============================================================
ZotEvent - CS122A Project
==============================================================

A command-line program that manages the ZotEvent platform on top of a
MySQL database. It reads command-line arguments, turns them into SQL,
runs them against MySQL, and prints the results.


--------------------------------------------------------------
1. PROJECT FILES
--------------------------------------------------------------
All files live at the top level of the repo (no subfolders):

  project.py        Entry point. Parses the command and dispatches it.
  common.py         Shared DB connection, output/parse helpers, schema.
  importer.py       import, updateEvent, deleteOrganizer.
  inserts.py        insertAdmin, addVenue, venueEvents.
  reservations.py   reserveSlot, cancelReservation, participantSchedule.
  reports.py        availableEvents, popularEventTypes, organizerStats.

When zipping for submission, keep all six files at the ROOT of the zip.
If they end up inside a folder, the imports between modules break on
the autograder.


--------------------------------------------------------------
2. MYSQL SETUP (one time, per machine)
--------------------------------------------------------------
Requirements:
  - Python 3
  - mysql-connector-python  (the only third-party Python package allowed)
  - A running MySQL 8.x server

Steps:

  a) Install Python 3 from python.org. On Windows, check
     "Add python.exe to PATH" during install.

  b) Install MySQL 8.x Community Server. Use the full MySQL Installer
     (not the web installer). During configuration, set a root password
     and let MySQL run as a background service.

  c) Install the Python connector:
        pip install mysql-connector-python

  d) Create the database and the 'test' user so the local setup matches
     the autograder. Open the MySQL client, log in as root, and run:

        CREATE DATABASE cs122a;
        CREATE USER 'test'@'localhost' IDENTIFIED BY 'password';
        GRANT ALL PRIVILEGES ON cs122a.* TO 'test'@'localhost';
        FLUSH PRIVILEGES;

  The program connects with:
        user='test', password='password', database='cs122a'
  (defined in common.py -> get_conn). Do NOT change this before
  submitting; it is what the autograder uses.

Verify the whole chain with a quick connection test:

        import mysql.connector
        conn = mysql.connector.connect(user='test', password='password',
                                       database='cs122a')
        print(conn.is_connected())   # should print True


--------------------------------------------------------------
3. RUNNING THE PROGRAM
--------------------------------------------------------------
General form:

        python3 project.py <functionName> [param1] [param2] ...

On Windows the command is usually 'python' instead of 'python3':

        python project.py <functionName> [param1] [param2] ...

Wrap any argument that contains a space in quotes, e.g.
"Annual Club Showcase". Pass NULL (literally) for a null argument.

First, load the data (the data folder is provided separately and is
NOT part of the submission zip):

        python project.py import sample_data


--------------------------------------------------------------
4. FUNCTIONS
--------------------------------------------------------------
  import <folder>
  insertAdmin <uid> <email> <username> <joined> <firstname> <lastname>
  addVenue <eid> <vid> <is_primary>
  reserveSlot <eid> <snum> <uid>
  cancelReservation <eid> <snum> <uid>
  updateEvent <eid> <title> <datetime>
  deleteOrganizer <uid>
  availableEvents <date>
  popularEventTypes <N>
  participantSchedule <uid>
  organizerStats <N>
  venueEvents <vid>

Functions that change data print "Success" or "Fail".
Functions that return a table print one record per line, columns
separated by commas, with NULL shown for missing values.


--------------------------------------------------------------
5. QUICK VERIFICATION
--------------------------------------------------------------
After importing the sample data, this should print Success:

        python project.py import sample_data

And this query should return five rows in datetime order:

        python project.py availableEvents 2026-04-15

Expected:
        505,Volunteer Day,service,2026-05-18 09:00:00,2
        501,Cloud Systems Talk,academic,2026-06-10 13:00:00,2
        502,Data Engineering Meetup,technical,2026-06-12 16:00:00,2
        503,Campus Club Fair,social,2026-06-15 11:00:00,1
        504,Robotics Demo,technical,2026-07-01 15:30:00,2

See TESTING.md for the full set of test cases covering every function,
including edge cases and the SQL queries to confirm the results.


--------------------------------------------------------------
6. NOTES
--------------------------------------------------------------
- Several test functions change the data. Re-run
  "python project.py import sample_data" to reset to a clean state
  before a fresh round of testing.
- deleteOrganizer relies on ON DELETE CASCADE: deleting an organizer
  also removes their events, and those events' slots and hosting rows.
- The data folder used for grading is hidden; the sample folder is only
  for local testing.
