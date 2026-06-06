# ZotEvent — Test Plan

Custom test cases covering all twelve functions, run against the provided
`sample_data`. These are our own cases (not the examples from the project
spec) and include edge cases and SQL queries to confirm results.

**Conventions**
- Commands are shown as `python project.py ...` (use `python3` on macOS/Linux).
- "→" shows expected stdout. An empty result means **no output is printed**.
- Many write tests mutate the database. **Reset before each section** with:

```
python project.py import sample_data
```

---

## 1. import

```
python project.py import sample_data
```
→ `Success`

Confirm the row counts loaded correctly (MySQL client):

```sql
SELECT COUNT(*) FROM User;      -- 10
SELECT COUNT(*) FROM Event;     -- 6
SELECT COUNT(*) FROM Slot;      -- 18
SELECT COUNT(*) FROM Venue;     -- 5
SELECT COUNT(*) FROM Hosting;   -- 7
SELECT COUNT(*) FROM Approval;  -- 3
```

Re-running `import` on an already-loaded DB should still print `Success`
(it drops and recreates every table first).

---

## 2. insertAdmin

Reset first, then create a brand-new admin user:

```
python project.py insertAdmin 150 nina@uci.edu nina_admin 2025-03-10 Nina Patel
```
→ `Success`

Confirm both rows were written:

```sql
SELECT * FROM User WHERE uid = 150;            -- 150, nina@uci.edu, nina_admin, 2025-03-10
SELECT * FROM Administrator WHERE uid = 150;   -- 150, Nina, Patel
```

Duplicate uid is rejected (151 does not exist, but 101 already does):

```
python project.py insertAdmin 101 dup@uci.edu dup 2025-01-01 Dup User
```
→ `Fail`

Edge — an existing non-admin user cannot be re-inserted (uid 104 is already
a User), because this function always inserts a new User row:

```
python project.py insertAdmin 104 dave2@uci.edu dave2 2025-01-01 Dave Two
```
→ `Fail`

---

## 3. addVenue

Reset first.

Add a secondary (non-primary) venue to an event that already has a primary:

```
python project.py addVenue 502 304 false
```
→ `Success`  (event 502's primary is 303; 304 is added as non-primary)

Reject a second primary venue for an event that already has one:

```
python project.py addVenue 503 301 true
```
→ `Fail`  (event 503 already has primary venue 302)

Reject a duplicate (eid, vid) pairing:

```
python project.py addVenue 501 301 false
```
→ `Fail`  ((501, 301) already exists in Hosting)

> Note: every event in the sample data already has a primary venue, so a
> successful `is_primary = true` add cannot be shown on this dataset. To
> exercise that path, use an event with no primary venue.

---

## 4. reserveSlot

Reset first.

Reserve a currently-open slot for an existing participant:

```
python project.py reserveSlot 502 2 110
```
→ `Success`

Confirm it:

```sql
SELECT * FROM Slot WHERE eid = 502 AND snum = 2;   -- 502, 2, 1, 110
```

Reserving it again fails (now reserved):

```
python project.py reserveSlot 502 2 110
```
→ `Fail`

Reserving an already-reserved slot fails:

```
python project.py reserveSlot 501 1 110
```
→ `Fail`  (slot 501/1 is already reserved by 104)

---

## 5. cancelReservation

Reset first.

Cancel a reservation held by the correct participant:

```
python project.py cancelReservation 504 2 105
```
→ `Success`

Confirm the slot is freed:

```sql
SELECT * FROM Slot WHERE eid = 504 AND snum = 2;   -- 504, 2, 0, NULL
```

Wrong participant cannot cancel:

```
python project.py cancelReservation 504 1 105
```
→ `Fail`  (slot 504/1 is reserved by 110, not 105)

Cancelling a slot that is not reserved fails:

```
python project.py cancelReservation 504 3 105
```
→ `Fail`  (slot 504/3 is open)

---

## 6. updateEvent

Reset first.

Update an existing event's title and datetime:

```
python project.py updateEvent 503 "Annual Club Showcase" "2026-06-20 10:30:00"
```
→ `Success`

Confirm:

```sql
SELECT title, datetime FROM Event WHERE eid = 503;
-- Annual Club Showcase | 2026-06-20 10:30:00
```

Updating a nonexistent event fails:

```
python project.py updateEvent 777 "Ghost Event" "2026-01-01 09:00:00"
```
→ `Fail`

---

## 7. deleteOrganizer

Reset first.

Delete an organizer and confirm the cascade. Organizer 108 created events
504 and 506:

```
python project.py deleteOrganizer 108
```
→ `Success`

Confirm events, slots, and hosting rows were cascaded away, but the
underlying User row remains:

```sql
SELECT eid FROM Event WHERE creator_uid = 108;        -- (empty)
SELECT * FROM Slot WHERE eid IN (504, 506);           -- (empty)
SELECT * FROM Hosting WHERE eid IN (504, 506);        -- (empty)
SELECT * FROM Organizer WHERE uid = 108;              -- (empty)
SELECT uid FROM User WHERE uid = 108;                 -- 108 (still present)
```

Deleting again fails (already gone):

```
python project.py deleteOrganizer 108
```
→ `Fail`

Deleting a uid that is not an organizer fails (104 is a participant):

```
python project.py deleteOrganizer 104
```
→ `Fail`

---

## 8. availableEvents

Reset first. (Read-only — order is datetime asc, then eid asc.)

Only events on/after the date that still have an open slot:

```
python project.py availableEvents 2026-06-13
```
→
```
503,Campus Club Fair,social,2026-06-15 11:00:00,1
504,Robotics Demo,technical,2026-07-01 15:30:00,2
```

A broader date returns all five events with open slots (506 is excluded
because all its slots are reserved):

```
python project.py availableEvents 2026-04-15
```
→
```
505,Volunteer Day,service,2026-05-18 09:00:00,2
501,Cloud Systems Talk,academic,2026-06-10 13:00:00,2
502,Data Engineering Meetup,technical,2026-06-12 16:00:00,2
503,Campus Club Fair,social,2026-06-15 11:00:00,1
504,Robotics Demo,technical,2026-07-01 15:30:00,2
```

A date past every event returns nothing:

```
python project.py availableEvents 2027-01-01
```
→ (empty)

---

## 9. popularEventTypes

Reset first. (Read-only — order is count desc, then type asc.)

Reserved-slot totals by type are academic 4, technical 3, social 2,
service 0.

```
python project.py popularEventTypes 1
```
→
```
academic,4
technical,3
social,2
```

Raising the threshold trims the list:

```
python project.py popularEventTypes 3
```
→
```
academic,4
technical,3
```

A threshold above every count returns nothing:

```
python project.py popularEventTypes 6
```
→ (empty)

---

## 10. participantSchedule

Reset first. (Read-only — order is datetime asc.)

Participant 105 reserved slots in events 501 and 504:

```
python project.py participantSchedule 105
```
→
```
501,Cloud Systems Talk,academic,2026-06-10 13:00:00,3,301,123 Ring Mall,Irvine,CA,92697
504,Robotics Demo,technical,2026-07-01 15:30:00,2,304,15 Ocean Ave,Newport Beach,CA,92660
```

Participant 106 reserved slots in events 502 and 506:

```
python project.py participantSchedule 106
```
→
```
506,Spring Research Review,academic,2026-04-01 10:00:00,2,301,123 Ring Mall,Irvine,CA,92697
502,Data Engineering Meetup,technical,2026-06-12 16:00:00,1,303,789 Engineering Quad,Irvine,CA,92697
```

A uid with no reservations returns nothing:

```
python project.py participantSchedule 999
```
→ (empty)

Edge — exercise the "no primary venue" branch (venue columns become NULL).
In the MySQL client, demote event 503's primary venue, then query
participant 109 (who reserved a slot in 503):

```sql
UPDATE Hosting SET is_primary = 0 WHERE eid = 503 AND vid = 302;
```
```
python project.py participantSchedule 109
```
→
```
503,Campus Club Fair,social,2026-06-15 11:00:00,2,NULL,NULL,NULL,NULL,NULL
```
Then reset with `python project.py import sample_data`.

---

## 11. organizerStats

Reset first. (Read-only — order is count desc, then uid asc.)

Each organizer created exactly two events, so a threshold of 2 lists all:

```
python project.py organizerStats 2
```
→
```
102,bob_sample,ICS,2
103,carol_sample,Student Affairs,2
108,henry_sample,Engineering,2
```

A threshold above every count returns nothing:

```
python project.py organizerStats 4
```
→ (empty)

---

## 12. venueEvents

Reset first. (Read-only — order is datetime asc, then eid asc.)

Venue 302 hosts event 501 (non-primary) and event 503 (primary):

```
python project.py venueEvents 302
```
→
```
501,Cloud Systems Talk,academic,2026-06-10 13:00:00,0
503,Campus Club Fair,social,2026-06-15 11:00:00,1
```

Venue 304 hosts a single event:

```
python project.py venueEvents 304
```
→
```
504,Robotics Demo,technical,2026-07-01 15:30:00,1
```

A venue that hosts nothing returns nothing:

```
python project.py venueEvents 999
```
→ (empty)

---

## Final reset

After running the write tests, restore a clean database before committing:

```
python project.py import sample_data
```
