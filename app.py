import os

from dotenv import load_dotenv
from static.queue_types import *
from flask import Flask, abort, redirect, render_template, request, url_for, flash
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Service, Ticket as DatabaseTicket, TicketItem, db

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-only-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)

SERVICES: list[ServiceDict] = [
    {
        "id": 1,
        "name": "To Check",
        "info": {"completed": "Your items have been checked and are ready for the next action."},
    },
    {
        "id": 2,
        "name": "To Ship",
        "info": {"completed": "Your items are ready to deliver."},
    },
]

TICKETS: list[Ticket] = [
    Ticket(number=1, name="Alex", service_id=1, items=[Item(name= "Ball", count=1, info="its a ball")], status="Waiting"),
]

def getQueuePlacement() -> int:
    return TICKETS[-1].number if TICKETS else 0

def getNextPlacement() -> int:
    return getQueuePlacement() + 1

@app.route("/")
def index():
    return render_template("index.html", name="", tickets=TICKETS)

@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = next((t for t in TICKETS if t.number == ticket_id), None)
    if t is None:
        abort(404)
    ahead = [x for x in TICKETS
             if x.service_id == t.service_id
             and x.status == "Waiting"
             and x.number < t.number]
    service = next(s for s in SERVICES if s["id"] == t.service_id)
    return render_template("ticket.html", ticket=t, service=service, ahead=len(ahead))

@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    t = next((t for t in TICKETS if t.number == ticket_id), None)
    if t is None:
        abort(404)
    t.status = "No-Show"
    flash(f"Ticket #{ticket_id} has left the queue.", "success")
    return redirect(url_for("index"))

@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    service_id = form.get("service_id", type=int)

    item_names = [item.strip() for item in form.getlist("items[]")]
    count_values = form.getlist("counts[]")
    count_values = (count_values + [""] * len(item_names))[:len(item_names)]
    item_counts = []

    errors = {}
    if not name:
        errors["name"] = "Enter your name."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Choose a service."
    if not item_names or any(not item for item in item_names):
        errors["items"] = "Enter a name for each item."
    for value in count_values:
        try:
            count = int(value)
        except ValueError:
            count = 0
        if count < 1:
            errors["counts"] = "Enter a whole-number quantity of at least 1 for each item."
        item_counts.append(count)

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template(
            "join.html",
            services=SERVICES,
            form=form,
            errors=errors,
            item_values=item_names or [""],
            count_values=count_values or ["1"],
        ), 400

    number = getNextPlacement()
    TICKETS.append(Ticket(
        number=number,
        name=name,
        service_id=service_id,
        items=[
            Item(name=item, count=count, info="")
            for item, count in zip(item_names, item_counts)
        ],
        status="Waiting",
    ))

    print(TICKETS[number-1])
    
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))

@app.route("/hello")
def hello():
    return "Hello, CCC181!"

@app.get("/join")
def join_form():
    return render_template(
        "join.html",
        services=SERVICES,
        form={},
        item_values=[""],
        count_values=["1"],
    )

@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    queue = [t for t in TICKETS if t.status in ("Waiting", "Processing")]

    if service_id is not None:
        queue = [t for t in queue if t.service_id == service_id]
    queue.sort(key=lambda ticket: ticket.number)
    waiting_count = sum(ticket.status == "Waiting" for ticket in queue)
    current_ticket = next(
        (ticket for ticket in queue if ticket.status == "Processing"),
        None,
    )

    names = {s["id"]: s["name"] for s in SERVICES}
    waiting_counts = {
        service["id"]: sum(
            ticket.service_id == service["id"] and ticket.status == "Waiting"
            for ticket in TICKETS
        )
        for service in SERVICES
    }
    return render_template("staff.html", queue=queue, services=SERVICES,
                           names=names, selected=service_id,
                           waiting_counts=waiting_counts,
                           waiting_count=waiting_count,
                           current_ticket=current_ticket)


@app.post("/staff/call-next")
def staff_call_next():
    service_id = request.form.get("service_id", type=int)
    waiting = [
        ticket for ticket in TICKETS
        if ticket.status == "Waiting"
        and (service_id is None or ticket.service_id == service_id)
    ]
    next_ticket = min(waiting, key=lambda ticket: ticket.number, default=None)

    if next_ticket is None:
        flash("There are no waiting tickets for this service.", "warning")
    else:
        next_ticket.status = "Processing"
        flash(f"Ticket #{next_ticket.number} has been called.", "success")

    return redirect(url_for("staff_dashboard", service_id=service_id))

staff_status_call: dict[Literal["call", "serve", "no-show"], status_types] = {
    "call": "Processing",
    "serve": "Completed",
    "no-show": "No-Show",
}

@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = staff_status_call.get(action)
    t = next((t for t in TICKETS if t.number == ticket_id), None)

    if t is None or new_status is None:
        abort(404)

    t.status = new_status

    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    service_id = request.form.get("service_id", type=int)
    return redirect(url_for("staff_dashboard", service_id=service_id))

@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = next((t for t in TICKETS if t.number == ticket_id), None)
    if t is None:
        abort(404)
    service = next(s for s in SERVICES if s["id"] == t.service_id)
    ahead = sum(1 for x in TICKETS
                if x.service_id == t.service_id
                and x.status == "Waiting" and x.number < t.number)
    
    return {
        "status": t.status,
        "ahead": ahead,
        "completion_message": service["info"]["completed"],
    }

@app.cli.command("seed")
def seed():
    """Add the starting services if they are not there yet."""

    for service in SERVICES:
        name = service["name"]
        exists = db.session.scalar(db.select(Service).filter_by(name=name))

        if exists is None:
            new_service = Service()
            new_service.name = name
            new_service.completed_message = service["info"]["completed"]
            db.session.add(new_service)

    db.session.commit()
    print("Services are ready.")

if __name__ == "__main__":
    app.run(debug=True)