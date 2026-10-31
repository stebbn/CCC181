import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Service, TicketItem, User, db
from models import Ticket as DatabaseTicket
from static.queue_types import *

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-only-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def index():
    tickets = db.session.scalars(
        db.select(DatabaseTicket).order_by(DatabaseTicket.id.desc())
    ).all()
    return render_template("index.html", name="", tickets=tickets)


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.session.get(DatabaseTicket, ticket_id)
    if t is None:
        abort(404)
    ahead = db.session.scalar(
        db.select(func.count())
        .select_from(DatabaseTicket)
        .where(
            DatabaseTicket.service_id == t.service_id,
            DatabaseTicket.status == "Waiting",
            DatabaseTicket.id < t.id,
        )
    )
    return render_template(
        "ticket.html",
        ticket=t,
        service=t.service,
        ahead=ahead or 0,
    )


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    t = db.session.get(DatabaseTicket, ticket_id)
    if t is None:
        abort(404)
    if t.status != "Waiting":
        abort(409)
    t.status = "Left"
    t.left_at = datetime.now(timezone.utc)
    db.session.commit()
    flash(f"Ticket #{ticket_id} has left the queue.", "success")
    return redirect(url_for("index"))


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)
    service: Service | None = (
        db.session.get(Service, service_id) if service_id else None
    )

    item_names = [item.strip() for item in form.getlist("items[]")]
    count_values = form.getlist("counts[]")
    count_values = (count_values + [""] * len(item_names))[: len(item_names)]
    item_quantities = []
    errors = {}

    if not name or len(name) > 120:
        errors["name"] = "Enter your name (up to 120 characters)."
    if (
        not email
        or len(email) > 254
        or "@" not in email
        or email.startswith("@")
        or email.endswith("@")
    ):
        errors["email"] = "Enter a valid email address."
    if service is None or not service.is_active:
        errors["service_id"] = "Choose an active service."
    if not item_names or any(not item or len(item) > 120 for item in item_names):
        errors["items"] = "Enter an item name of up to 120 characters for each item."

    for value in count_values:
        try:
            quantity = int(value)
        except ValueError:
            quantity = 0
        if quantity < 1:
            errors["counts"] = (
                "Enter a whole-number quantity of at least 1 for each item."
            )
        item_quantities.append(quantity)

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return (
            render_template(
                "join.html",
                services=all_services(),
                form=form,
                errors=errors,
                item_values=item_names or [""],
                count_values=count_values or ["1"],
            ),
            400,
        )

    if service is None:
        abort(400)

    user: User | None = db.session.scalar(db.select(User).filter_by(email=email))
    if user is not None and (user.role != "driver" or not user.is_active):
        errors["email"] = (
            "That email is not available for an active driver account."
        )
        return (
            render_template(
                "join.html",
                services=all_services(),
                form=form,
                errors=errors,
                item_values=item_names or [""],
                count_values=count_values or ["1"],
            ),
            400,
        )

    if user is None:
        user = User()
        user.name = name
        user.email = email
        user.role = "driver"
        db.session.add(user)
    else:
        user.name = name

    ticket_record: DatabaseTicket = DatabaseTicket()
    ticket_record.driver = user
    ticket_record.service = service
    ticket_record.items = []
    for item_name, quantity in zip(item_names, item_quantities):
        ticket_item = TicketItem()
        ticket_item.item_name = item_name
        ticket_item.quantity = quantity
        ticket_record.items.append(ticket_item)
    db.session.add(ticket_record)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        app.logger.exception("Could not save a queue ticket")
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        return (
            render_template(
                "join.html",
                services=all_services(),
                form=form,
                errors={},
                item_values=item_names or [""],
                count_values=count_values or ["1"],
            ),
            409,
        )

    flash(f"You joined the queue. Your ticket is #{ticket_record.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket_record.id))


@app.get("/join")
def join_form():
    return render_template(
        "join.html",
        services=all_services(),
        form={},
        item_values=[""],
        count_values=["1"],
    )


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = db.session.get(DatabaseTicket, ticket_id)
    if t is None:
        abort(404)
    ahead = db.session.scalar(
        db.select(func.count())
        .select_from(DatabaseTicket)
        .where(
            DatabaseTicket.service_id == t.service_id,
            DatabaseTicket.status == "Waiting",
            DatabaseTicket.id < t.id,
        )
    )

    return {
        "status": t.status,
        "ahead": ahead or 0,
        "completion_message": t.service.completed_message,
    }


# Staff ----------------------------------------------------------------------------------------


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    statement = db.select(DatabaseTicket).where(
        DatabaseTicket.status.in_(("Waiting", "Processing"))
    )
    if service_id is not None:
        statement = statement.where(DatabaseTicket.service_id == service_id)
    queue = db.session.scalars(statement.order_by(DatabaseTicket.id)).all()
    waiting_count = sum(ticket.status == "Waiting" for ticket in queue)
    current_ticket = next(
        (ticket for ticket in queue if ticket.status == "Processing"),
        None,
    )

    return render_template(
        "staff.html",
        queue=queue,
        services=db.session.scalars(
            db.select(Service).order_by(Service.name)
        ).all(),
        selected=service_id,
        waiting_count=waiting_count,
        current_ticket=current_ticket,
    )


@app.post("/staff/call-next")
def staff_call_next():
    service_id = request.form.get("service_id", type=int)
    statement = db.select(DatabaseTicket).where(
        DatabaseTicket.status == "Waiting"
    )
    if service_id is not None:
        statement = statement.where(DatabaseTicket.service_id == service_id)
    next_ticket = db.session.scalar(
        statement.order_by(DatabaseTicket.id)
        .with_for_update(skip_locked=True)
        .limit(1)
    )

    if next_ticket is None:
        flash("There are no waiting tickets for this service.", "warning")
    else:
        next_ticket.status = "Processing"
        next_ticket.called_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f"Ticket #{next_ticket.id} has been called.", "success")

    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    t = db.session.get(DatabaseTicket, ticket_id)
    if t is None:
        abort(404)

    now = datetime.now(timezone.utc)
    if action == "serve" and t.status == "Processing":
        t.status = "Completed"
        t.completed_at = now
    elif action == "no-show" and t.status == "Waiting":
        t.status = "No-Show"
        t.no_show_at = now
    else:
        abort(404)

    db.session.commit()
    flash(f"Ticket #{ticket_id} marked {t.status}.", "info")
    service_id = request.form.get("service_id", type=int)
    return redirect(url_for("staff_dashboard", service_id=service_id))


# Utils plz ----------------------------------------------------------------------------------


@app.cli.command("seed")
def seed():
    """Add the starting services if they are not there yet."""

    for name, completed_message in (
        (
            "To Check",
            "Your items have been checked and are ready for the next action.",
        ),
        ("To Ship", "Your items are ready to deliver."),
    ):
        exists = db.session.scalar(db.select(Service).filter_by(name=name))

        if exists is None:
            new_service = Service()
            new_service.name = name
            new_service.completed_message = completed_message
            db.session.add(new_service)

    db.session.commit()
    print("Services are ready.")


def all_services():
    return db.session.scalars(
        db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
    ).all()


if __name__ == "__main__":
    app.run(debug=True)
