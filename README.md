# WarehouseQ

WarehouseQ is a Flask queue for warehouse item checking and shipment processing. Drivers choose **To Check** or **To Ship**, enter their name, and list their items and quantities. Staff can view tickets in order, call the next ticket, and update its status.

Project requirements are documented in [docs/requirements.md](docs/requirements.md).

## Run locally with Docker

From the project root, copy the example environment file. If you change the
example password, use the same password in both environment variables:

```powershell
Copy-Item .env.example .env
# Edit .env and set a private password for local development.
docker compose up -d
docker compose ps
```

Wait until the database reports **healthy**. Then create the virtual environment,
install the dependencies, apply the migrations, seed the starting services, and
start Flask:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app db upgrade
flask --app app seed
flask --app app run --debug
```

Open <http://127.0.0.1:5000>. The staff dashboard is at <http://127.0.0.1:5000/staff>.

Staff routes are currently open without authentication. Track the planned Week 11
protection in [issue #4](https://github.com/stebbn/CCC181/issues/4).

## Project layout

- `app.py`, `queue_types.py`, and `requirements.txt` are at the project root.
- `templates/` and `static/` contain the Flask pages and assets.
- `assets/` contains shared images and test evidence.
