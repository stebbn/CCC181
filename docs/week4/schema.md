# WarehouseQ database schema

This is the proposed schema for WarehouseQ's warehouse receiving workflow. It models the current queue and the warehouse-specific requirements, including stored item lines and the planned service-management, priority, and no-show reporting features. `users` is not included: WarehouseQ currently collects a driver name for each ticket but has no accounts, email addresses, or reusable driver profile.

## Find the nouns in the requirements

Each requirement marked **Stores data? = Yes** in [the requirements list](../requirements.md) is included below. The queue and the number of people ahead are derived from tickets; they are not stored as separate records or columns.

| Req ID | Requirement | Nouns | Table or column? |
| --- | --- | --- | --- |
| REQ-C01 | A driver can join the To Check or To Ship queue by entering their name and the items and quantities for the request. | **driver**, **queue**, **service**, **name**, **items**, **quantities**, **request** | **driver** name → `tickets.driver_name`; **queue** → computed from `tickets`; **service** → `services`, referenced by `tickets.service_id`; **request** → `tickets`; **items** → `ticket_items.item_name`; **quantities** → `ticket_items.quantity` |
| REQ-C02 | A driver can view their ticket number, selected service, current status, and how many people are ahead in that service. | **ticket number**, **service**, **status**, **people ahead** | **ticket number** → `tickets.id`; **service** → `tickets.service_id` and `services.name`; **status** → `tickets.status`; **people ahead** → computed from earlier waiting tickets for the same service |
| REQ-C03 | A driver can tell when staff have called their ticket by seeing its status change to Processing on the ticket page. | **driver**, **staff**, **ticket**, **status** | **ticket** → `tickets`; **status** → `tickets.status` and `tickets.called_at`; **driver** and **staff** are actors, not persisted account records in this app |
| REQ-S01 | A warehouse staff member can view waiting tickets in ticket-number order on the staff dashboard. | **staff member**, **tickets**, **ticket-number order** | **tickets** → `tickets`; **ticket-number order** → generated `tickets.id`; **staff member** is an actor, not a stored user |
| REQ-S02 | A warehouse staff member can identify whether each ticket is for To Check or To Ship from its service label. | **staff member**, **ticket**, **service**, **service label** | **ticket** → `tickets`; **service** and **service label** → `services`, referenced by `tickets.service_id` |
| REQ-S03 | A warehouse staff member can call the next waiting ticket and update its status to Completed or No-Show from the dashboard. | **staff member**, **ticket**, **status**, **call**, **service** | **ticket** and **status** → `tickets`; **call**, completion, and no-show times → `tickets.called_at`, `tickets.completed_at`, `tickets.no_show_at`; **service** → `tickets.service_id`; **staff member** is an actor, not a stored user |
| REQ-S04 | WarehouseQ can save services, tickets, item names, quantities, and statuses so the queue is still available after the server restarts. | **services**, **tickets**, **item names**, **quantities**, **statuses**, **queue** | **services** → `services`; **tickets** and **statuses** → `tickets`; **item names** and **quantities** → `ticket_items`; **queue** → computed from stored tickets |
| REQ-C04 | A driver can review the item names and quantities on their ticket after joining the queue. | **driver**, **item names**, **quantities**, **ticket** | **ticket** → `tickets`; **item names** and **quantities** → `ticket_items`; **driver** is an actor identified on that ticket by `tickets.driver_name` |
| REQ-C05 | A driver can mark a request as time-sensitive so staff can identify it on the dashboard and prioritize it within its service. | **driver**, **request**, **priority**, **staff**, **service** | **request** → `tickets`; **priority** → `tickets.is_priority`; **service** → `tickets.service_id`; **driver** and **staff** are actors |
| REQ-S05 | A warehouse staff member can add a service, rename it, or switch it off so drivers cannot select it for new tickets. | **staff member**, **service**, **name**, **active state**, **drivers** | **service**, **name**, and **active state** → `services.id`, `services.name`, and `services.is_active`; **staff member** and **drivers** are actors |
| REQ-S06 | A warehouse staff member can see the number of No-Show tickets for each service on a selected day. | **staff member**, **No-Show tickets**, **service**, **day**, **number** | **tickets** → `tickets`; **service** → `tickets.service_id`; **day** → `tickets.no_show_at` (`timestampt`); **number** → computed count, not stored; **staff member** is an actor |

## Tables and columns

Three related tables are needed. A ticket is one warehouse request, and each item/quantity pair is a separate row so tickets can contain any number of items.

| Table | Columns |
| --- | --- |
| `services` | `id`, `name`, `completed_message`, `is_active`, `created_at` |
| `tickets` | `id`, `driver_name`, `service_id`, `status`, `is_priority`, `created_at`, `called_at`, `completed_at`, `no_show_at`, `left_at` |
| `ticket_items` | `id`, `ticket_id`, `item_name`, `quantity` |

The driver's name is stored on the ticket because it is the name supplied for that request; WarehouseQ does not currently have driver accounts or email addresses. Service details are kept separately so a service can be renamed or disabled without copying its name to every ticket. Ticket item names and quantities are kept in `ticket_items`, one row per item line.

The ticket status uses `Waiting`, `Processing`, `Completed`, `No-Show`, or `Left`. `Left` distinguishes a driver who leaves the queue from a driver who fails to appear, allowing no-show reports to count only actual no-shows. `is_priority` supports the future priority feature. `is_active` supports disabling a service while retaining it for historical tickets.

Queue position and counts are computed, not stored. The position is the count of earlier `Waiting` tickets for the same service, ordered by `created_at` and then `id` to break ties. The no-show count is computed from `tickets.no_show_at` for the selected service and day.

## PostgreSQL types and constraints

`GENERATED ALWAYS AS IDENTITY` columns are generated by PostgreSQL. All timestamp columns use `timestampt`; nullable transition times are filled when that transition occurs.

| Table | Column | PostgreSQL type | Constraint | Why |
| --- | --- | --- | --- | --- |
| `services` | `id` | `bigint GENERATED ALWAYS AS IDENTITY` | PRIMARY KEY | Stable generated identifier for each service. |
| `services` | `name` | `varchar(80)` | NOT NULL, UNIQUE | Required service label; prevents duplicate labels such as two `To Check` services. |
| `services` | `completed_message` | `varchar(250)` | NOT NULL | Stores the service-specific completion message shown to the driver. |
| `services` | `is_active` | `boolean` | NOT NULL DEFAULT `true` | Inactive services stay available for old tickets but cannot be chosen for new ones. |
| `services` | `created_at` | `timestampt` | NOT NULL DEFAULT `now()` | Records when the service was created, using a time-zone-aware timestamp. |
| `tickets` | `id` | `bigint GENERATED ALWAYS AS IDENTITY` | PRIMARY KEY | Unique ticket number generated by the database. |
| `tickets` | `driver_name` | `varchar(120)` | NOT NULL | Stores the name entered for this warehouse request. |
| `tickets` | `service_id` | `bigint` | NOT NULL, FOREIGN KEY REFERENCES `services(id)` ON DELETE RESTRICT | Every ticket must belong to an existing service; deleting a service cannot erase ticket history. |
| `tickets` | `status` | `varchar(20)` | NOT NULL DEFAULT `'Waiting'`, CHECK (`status` IN (`'Waiting'`, `'Processing'`, `'Completed'`, `'No-Show'`, `'Left'`)) | Restricts ticket state to the states used by the queue workflow. |
| `tickets` | `is_priority` | `boolean` | NOT NULL DEFAULT `false` | Stores whether this individual request has priority; it can vary per ticket. |
| `tickets` | `created_at` | `timestampt` | NOT NULL DEFAULT `now()` | Records when the ticket joined; used to order the queue and compute position. |
| `tickets` | `called_at` | `timestampt` | NULL allowed | Records when the ticket was called; NULL until called. |
| `tickets` | `completed_at` | `timestampt` | NULL allowed | Records when staff completed the work; NULL unless completed. |
| `tickets` | `no_show_at` | `timestampt` | NULL allowed | Records when staff marked a no-show; supports per-service, per-day reports. |
| `tickets` | `left_at` | `timestampt` | NULL allowed | Records when a driver left before being called, separately from a no-show. |
| `ticket_items` | `id` | `bigint GENERATED ALWAYS AS IDENTITY` | PRIMARY KEY | Gives each item line its own stable identifier. |
| `ticket_items` | `ticket_id` | `bigint` | NOT NULL, FOREIGN KEY REFERENCES `tickets(id)` ON DELETE CASCADE | Associates the item line with its ticket; ticket items have no meaning without their ticket. |
| `ticket_items` | `item_name` | `varchar(120)` | NOT NULL | Stores one item description per row. |
| `ticket_items` | `quantity` | `integer` | NOT NULL, CHECK (`quantity` > 0) | Stores a numeric, positive item quantity. |

This schema uses PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK, and `timestampt`. Ticket positions, counts, and service queues are query results rather than stored values.

## 2d. Entity relationship diagram

![WarehouseQ entity relationship diagram](erd.png)

**Relationships:** One service has many tickets. Each ticket belongs to exactly one service. One ticket has many item lines. Each item line belongs to exactly one ticket.

**Foreign-key deletion behavior:**

- `tickets.service_id` references `services.id` with **ON DELETE RESTRICT**. A service with ticket history cannot be deleted, preserving reports and old requests. Staff can switch it off with `services.is_active` instead.
- `ticket_items.ticket_id` references `tickets.id` with **ON DELETE CASCADE**. Item lines are dependent details of a ticket and should not remain as orphan rows if a ticket is deleted.

There are no many-to-many relationships in this version of WarehouseQ.

## 2e. Normalization check

1. **One value per cell (1NF):** Yes. Each ticket item and quantity is one `ticket_items` row. A ticket does not contain a comma-separated list of item names or quantities.
2. **Depends on the whole key (2NF):** There is no join table with a composite key. Every non-key column in each table describes its row's primary key; the fields in `ticket_items` describe that item line.
3. **No hidden copies (3NF):** Service name and completion message are stored once in `services`, rather than repeated on every ticket. Each item line belongs to one ticket. A driver's name is recorded on each ticket as the name provided for that request; there is no separate driver account or profile fact duplicated across records.