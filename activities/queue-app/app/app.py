from queue_types import *
from flask import Flask, abort, redirect, render_template, request, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-only-change-me"


SERVICES: list[ServiceDict] = [
    {"id": 1, "name": "To Check"},
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

@app.route("/staff")
def staff_dashboard():
    return "Staff dashboard coming soon"

if __name__ == "__main__":
    app.run(debug=True)