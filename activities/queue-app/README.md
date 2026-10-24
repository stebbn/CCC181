# WarehouseQ

WarehouseQ is a Flask queue for warehouse item checking and shipment processing. Drivers choose **To Check** or **To Ship**, enter their name, and list their items and quantities. Staff can view tickets in order, call the next ticket, and update its status.

## Run locally

From the project root, create and activate a virtual environment, install the dependencies, and start Flask:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app run --debug
```

Open <http://127.0.0.1:5000>. The staff dashboard is at <http://127.0.0.1:5000/staff>.

## Project layout

- `app.py`, `queue_types.py`, and `requirements.txt` are at the project root.
- `templates/` and `static/` contain the Flask pages and assets.
- `assets/` contains shared images and test evidence.
