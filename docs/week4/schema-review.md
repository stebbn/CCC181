# WarehouseQ schema self-review

The schema was set aside for at least an hour before this review. I checked it against the requirements and Week 3 persona tasks, then updated the schema and ERD to address the issues below.

## Review findings

### Queue order and requirement coverage

**Works well:** `tickets` records the service and status needed to build each service's queue, and the number of people ahead is computed rather than stored.
<br>**Problem:** The schema described queue order by `created_at`, while REQ-S01 and the staff dashboard specify ticket-number order. This mismatch was found by question 1 (coverage).
<br>**Change:** Queue order and position are now defined by `tickets.id` (the ticket number). `created_at` remains for recording join time and date-based reporting.

### Status and transition timestamps

**Works well:** Separate transition timestamps preserve when a ticket was called, completed, marked No-Show, or left the queue, supporting status display and no-show reporting.
<br>**Problem:** Storing both `status` and transition timestamps without a consistency rule could allow contradictory data, such as a `Waiting` ticket with a completion time. This was found by question 2 (one fact in one place) and question 4 (bad data).
<br>**Change:** Added a table-level `CHECK` constraint in `schema.md` requiring transition timestamps to agree with the ticket status. Status and timestamp must be updated together.

### Column and type review

**Works well:** Service names and completion messages are stored once in `services`, while each ticket item is stored as its own row. This avoids repeated service facts and list-valued item columns.
<br>**Problem:** `services.created_at` was not needed by any current or planned requirement, and the timestamp type had been misspelled as `timestampt` in the schema since `timestamptz` includes the time and timezone. These were found by questions 1 (coverage) and 6 (types).
<br>**Change:** Removed `services.created_at` and corrected all timestamp columns and references to PostgreSQL's `timestamptz`.

### Foreign-key deletion behavior

**Works well:** Deleting a service with ticket history is restricted, and deleting a ticket cascades only to its dependent item lines. This preserves service and ticket history while preventing orphan item rows.
<br>**Problem:** No additional delete issue was found in the current three-table design.
<br>**Change:** Kept `ON DELETE RESTRICT` for `tickets.service_id` and `ON DELETE CASCADE` for `ticket_items.ticket_id`, with the reasons documented in `schema.md`.

## Other checks

- Queue position and no-show totals are computed instead of being stored.
- Primary keys prevent duplicate IDs, foreign keys reject missing services or tickets, status and quantity checks reject invalid values. The app must still validate that a selected service is active and is the service the driver intended.
- Names for services are stored once, ticket item rows contain one item and quantity, and there is no composite-key join table in this design.
