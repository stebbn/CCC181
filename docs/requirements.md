# WarehouseQ requirements

**Setting:** Warehouse receiving and loading bay during weekday business hours
**People who wait:** Alex, a logistics coordinator and delivery driver bringing items for checking or shipping ([persona](week3/personas.md#alex-the-person-waiting))
**People who serve:** Jade, a warehouse receiving specialist who processes and tracks the requests ([persona](week3/personas.md#jade-the-warehouse-staff-member))

**Problem statement:** Alex needs a way to join the correct service queue and check the request status and place in line while waiting because an unfamiliar, noisy warehouse makes it difficult to know when items are being processed or when it is their turn. Jade needs a clear, ordered view of requests and a simple way to call people and update ticket statuses because paper slips and interruptions make it difficult to process different types of requests accurately and in order.

## 1b. Functional requirements

| ID | Requirement | Priority | Stores data? | Status |
| --- | --- | --- | --- | --- |
| REQ-C01 ★ | A driver can join the **To Check** or **To Ship** queue by entering their name and the items and quantities for the request. | Must | **Yes** | Built (Week 3) |
| REQ-C02 | A driver can view their ticket number, selected service, current status, and how many people are ahead in that service. | Must | **Yes** | Built (Week 3) |
| REQ-C03 ★ | A driver can tell when staff have called their ticket by seeing its status change to Processing on the ticket page. | Must | **Yes** | Built (Week 3) |
| REQ-S01 | A warehouse staff member can view waiting tickets in ticket-number order on the staff dashboard. | Must | **Yes** | Built (Week 3) |
| REQ-S02 ★ | A warehouse staff member can identify whether each ticket is for **To Check** or **To Ship** from its service label. | Must | **Yes** | Built (Week 3) |
| REQ-S03 | A warehouse staff member can call the next waiting ticket and update its status to Completed or No-Show from the dashboard. | Must | **Yes** | Built (Week 3) |
| REQ-S04 | WarehouseQ can save services, tickets, item names, quantities, and statuses so the queue is still available after the server restarts. | Must | **Yes** | This week |
| REQ-C04 | A driver can review the item names and quantities on their ticket after joining the queue. | Should | **Yes** | Later |
| REQ-C05 ★ | A driver can mark a request as time-sensitive so staff can identify it on the dashboard and prioritize it within its service. | Could | **Yes** | Later |
| REQ-S05 | A warehouse staff member can add a service, rename it, or switch it off so drivers cannot select it for new tickets. | Should | **Yes** | Later |
| REQ-S06 | A warehouse staff member can see the number of No-Show tickets for each service on a selected day. | Should | **Yes** | Later |

The six requirements already used in the personas keep their original IDs. New customer requirements continue as REQ-C04, REQ-C05, and so on; new staff requirements continue as REQ-S04, REQ-S05, and so on. IDs are not reused or renumbered. Database persistence is planned for this week; the other new features are future work.

## 1c. Non-functional requirements

| ID | Requirement | Category | Priority |
| --- | --- | --- | --- |
| NFR-01 | No saved service, ticket, item, or status is lost when the Flask server or database restarts. | Reliability | Must |
| NFR-02 | Two simultaneous joins never receive the same ticket number. | Data integrity | Must |
| NFR-03 | The My place page finishes loading in under 2 seconds on a mobile connection. | Performance | Should |
| NFR-04 | Every app screen scores at least 90 in Lighthouse Accessibility. | Accessibility | Should |
| NFR-05 | No database password or secret key is stored in the repository. | Security | Must |

## 1d. MVP

**MVP:** REQ-C01, REQ-C02, REQ-C03, REQ-S01, REQ-S02, REQ-S03, REQ-S04, NFR-01, NFR-02, and NFR-05.

This is the smallest version that lets a driver submit items to the correct warehouse service and track the ticket, while staff can identify, call, and process requests in order. REQ-S04 and the non-functional requirements ensure the core queue and its data persist reliably.

**Out of scope this semester:**

- **SMS or automated phone notifications:** Drivers can check their ticket page for status updates; connecting a messaging provider would add external service costs and setup.
- **Barcode scanner integration:** Drivers enter item names and quantities on the join form, so scanner hardware and its integration are not needed for this semester's queue workflow.

## 1e. Check the requirements with a real person

The requirements were reviewed with a warehouse delivery driver. The notes below record their feedback and the resulting change.

| Who (role only, no full name) | What they said | What I changed |
| --- | --- | --- |
| Warehouse delivery driver | Nothing was identified as wrong or unimportant. They wanted to see the items on their ticket again. They did not choose three priorities, so my suggested top three are REQ-C01, REQ-C02, and REQ-C04 based on the core workflow and their feedback. | Added REQ-C04 for reviewing the item names and quantities on a ticket. |
