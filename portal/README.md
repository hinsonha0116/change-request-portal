# Change Request Portal: standalone version

A Django rebuild of the Power Apps portal, meant to run in a Kubernetes cluster with no Microsoft 365 services. The guides in the parent folder are the specification.

**Status:** steps 1 and 2 of 6 are done: the data model, the stage rules and the four screens (board, New Request, detail, schedule). Still to come: single sign-on, notifications and email, and the container image and Helm chart.

## What's here

| Path | Purpose |
|---|---|
| `accounts/` | Users and their roles (CM, TRB, CAB, Change Authority, SW and HW managers) |
| `changes/models.py` | Change requests, history, attachments and the CR number counter |
| `changes/services.py` | Submitting a request and giving it a number (`CR-2026-001`) |
| `changes/workflow.py` | Routes for each change type, who can do what, and every stage action |
| `changes/schedule.py` | The month grid and clash detection for the schedule |
| `changes/views.py`, `forms.py`, `templates/`, `static/` | The screens |
| `changes/management/commands/seed_demo.py` | Demo users and requests for local work |
| `changes/tests/` | Tests for every route, rule, permission and screen |
| `config/` | Settings, read from environment variables. `settings_dev.py` is for local work only |

## Run it locally

Needs Python 3.12 or newer. From this folder:

```bash
python -m venv .venv
```

```bash
.venv/Scripts/python -m pip install -r requirements.txt
```

Run the tests:

```bash
.venv/Scripts/python manage.py test --settings config.settings_dev
```

Create the local database and load the demo users and requests:

```bash
.venv/Scripts/python manage.py migrate --settings config.settings_dev
```

```bash
.venv/Scripts/python manage.py seed_demo --settings config.settings_dev
```

Start the app, then open http://localhost:8000:

```bash
.venv/Scripts/python manage.py runserver --settings config.settings_dev
```

The demo users are `pat` and `sam` (requesters), `cm`, `trb`, `cab` and `authority`. Their shared password is `DEMO_PASSWORD` in `changes/management/commands/seed_demo.py`. `cm` can also open the admin site at `/admin/` to add users and roles.

`config.settings_dev` turns debug on and uses a local SQLite file. The PostgreSQL driver is only installed on Linux (the container image).

## Settings

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Required unless `DJANGO_DEBUG=1` |
| `DJANGO_DEBUG` | `1` for local work only |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names the app answers to |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database connection. Leave `POSTGRES_HOST` unset to use SQLite |
| `PORTAL_MAX_UPLOAD_MB` | Largest single attachment. Default `25` |
| `PORTAL_TIME_ZONE` | Time zone for dates and the yearly CR number reset. Default `UTC` |
