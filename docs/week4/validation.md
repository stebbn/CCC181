# validation results
| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Name is required and at most 120 characters | Flask | Posted a 121-character name with the test client | Flask returned HTTP 400 and ticket count was unchanged |
| Email is required and valid, at most 254 characters | Flask | Posted `email=not-an-email` with otherwise valid fields | Flask returned HTTP 400 and ticket count was unchanged |
| Service must exist and be active | Flask | Posted `service_id=999` with otherwise valid fields | Flask returned HTTP 400 and ticket count was unchanged |
| Item name is required and at most 120 characters | Flask | Checked the rendered form and posted a 121-character item name | Form has `required` and `maxlength="120"`, Flask returned HTTP 400 and ticket count was unchanged |
| `tickets.service_id` must reference a service | Database | Inserted a ticket with a valid temporary driver and nonexistent service ID | `insert or update on table "tickets" violates foreign key constraint "tickets_service_id_fkey"` |
| User email must be unique | Database | Inserted a second user with the temporary driver's email | `duplicate key value violates unique constraint "users_email_key"` |
| Ticket status must be allowed | Database | Updated a temporary ticket to `status = 'lost'` | `new row for relation "tickets" violates check constraint "ck_tickets_status"` |
| Service average minutes must be positive | Database | Inserted a service with `avg_minutes = 0` | `new row for relation "services" violates check constraint "ck_services_avg_minutes"` |
| User name is required | Database | Inserted a user with `name = NULL` | `null value in column "name" of relation "users" violates not-null constraint` |
| A service with tickets cannot be deleted | Database | Deleted the temporary service while its temporary ticket referenced it | `update or delete on table "services" violates foreign key constraint "tickets_service_id_fkey" on table "tickets"` |
| Ticket item quantity must be positive | Database | Inserted a ticket item with `quantity = 0` | `new row for relation "ticket_items" violates check constraint "ck_ticket_items_quantity_positive"` |
| Ticket defaults are populated | Database | Inserted a valid temporary ticket and returned `id`, `status`, and `created_at` | Insert succeeded and PostgreSQL populated the ID and timestamp, and `status` was `Waiting` |
| SQL is not assembled in f-strings | Database | Ran `git grep -nE 'f.*(SELECT\|INSERT\|UPDATE\|DELETE)' -- '*.py'` | nothing |