from queue_types import *
from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

SERVICES: list[ServiceDict] = [
    {"id": 1, "name": "To Check"},
    {"id": 2, "name": "To Ship"},
]

TICKETS: list[Ticket] = [
    Ticket(number=1, name="Shampoo", source="producer_123_id", service_id=1, status="waiting"),
]

@app.route("/")
def index():
    return render_template("index.html", name="Shampoo", tickets=TICKETS)

@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    for position, t in enumerate(TICKETS, start=1):
        if t.number== ticket_id:
            return render_template("ticket.html", ticket=t, position=position)
    abort(404)

@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("join.html", error="Please enter your name.")

        new_number= TICKETS[-1].number+ 1 if TICKETS else 1
     
        new_ticket = Ticket(
            number=new_number,
            name=name,
            source="-",     
            service_id=1,       
            status="waiting"
        )
        
        TICKETS.append(new_ticket)
        return redirect(url_for("ticket", ticket_id=new_number))

    return render_template("join.html")

@app.route("/hello")
def hello():
    return "Hello, CCC181!"

if __name__ == "__main__":
    app.run(debug=True)