import sys
from common import to_none, to_bool
from importer import do_import, update_event, delete_organizer
from inserts import insert_admin, add_venue, venue_events
from reservations import reserve_slot, cancel_reservation, participant_schedule
from reports import available_events, popular_event_types, organizer_stats


def main():
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "import":
        do_import(args[0])
    elif cmd == "insertAdmin":
        insert_admin(int(args[0]), to_none(args[1]), to_none(args[2]), to_none(args[3]),to_none(args[4]), to_none(args[5]))
    elif cmd == "addVenue":
        add_venue(int(args[0]), int(args[1]), to_bool(args[2]))
    elif cmd == "reserveSlot":
        reserve_slot(int(args[0]), int(args[1]), int(args[2]))
    elif cmd == "cancelReservation":
        cancel_reservation(int(args[0]), int(args[1]), int(args[2]))
    elif cmd == "updateEvent":
        update_event(int(args[0]), to_none(args[1]), to_none(args[2]))
    elif cmd == "deleteOrganizer":
        delete_organizer(int(args[0]))
    elif cmd == "availableEvents":
        available_events(args[0])
    elif cmd == "popularEventTypes":
        popular_event_types(int(args[0]))
    elif cmd == "participantSchedule":
        participant_schedule(int(args[0]))
    elif cmd == "organizerStats":
        organizer_stats(int(args[0]))
    elif cmd == "venueEvents":
        venue_events(int(args[0]))

if __name__ == "__main__":
    main()
