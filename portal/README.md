# Change Request Portal: standalone version

A Django rebuild of the Power Apps portal, meant to run in a Kubernetes cluster with no Microsoft 365 services. The guides in the parent folder are the specification.

**Status:** steps 1 to 4 of 6 are done: the data model, the stage rules, the screens, sign-in and roles, and notifications with email. Still to come: the container image and Helm chart, then a full run in a local cluster.

## What's here

| Path | Purpose |
|---|---|
| `accounts/` | Users, their roles (CM, TRB, CAB, Change Authority, SW and HW managers), the People screen and single sign-on |
| `changes/models.py` | Change requests, history, attachments and the CR number counter |
| `changes/services.py` | Submitting a request and giving it a number (`CR-2026-001`) |
| `changes/workflow.py` | Routes for each change type, who can do what, and every stage action |
| `changes/notify.py` | Who is told about what, in the app and by email |
| `changes/schedule.py` | The month grid and clash detection for the schedule |
| `changes/views.py`, `forms.py`, `templates/`, `static/` | The screens: board, list, New Request, detail, schedule and notifications |
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

The demo users are `pat` and `sam` (requesters), `cm`, `trb`, `cab` and `authority`. `cm` holds every role and is a superuser, so that one account can approve and move a request through every step. Their shared password is `DEMO_PASSWORD` in `changes/management/commands/seed_demo.py`. `cm` can also open the admin site at `/admin/` to add users and roles.

`config.settings_dev` turns debug on and uses a local SQLite file. The PostgreSQL driver is only installed on Linux (the container image).

## Sign-in and roles

- **Local accounts** work out of the box. Create the first one with `manage.py createsuperuser`, then add people in the Admin site (`/admin/`). People can change their own password.
- **Single sign-on** switches on when the `OIDC_*` settings below are filled in. It works with any OpenID Connect provider. Register the portal with the provider as a confidential client with the redirect address `https://<portal host>/oidc/callback/`. A person's portal user is created the first time they sign in.
- **Roles** are set on the People screen, which the CM team and superusers can open. Roles can instead come from the provider's groups with `PORTAL_OIDC_ROLE_GROUPS`.
- Single sign-on is tested only as far as matching people and mapping groups. It has not been run against a real provider yet.

## Notifications

Everyone who needs to act on a request, or know about it, gets a notification in the app. When `EMAIL_HOST` is set the same message is emailed. A mail failure is logged and never blocks the change. With `config.settings_dev`, emails are printed in the terminal instead of sent.

| When | Who is told |
|---|---|
| New request | CM team; SW managers for Software; HW managers for Hardware |
| Reaches TRB, CAB or Change Authority | That board's members |
| Sent back to the requester, or TRB asks for changes | Requester |
| Reaches Implementation | Requester, with the CM team copied |
| Marked complete | CM team |
| Reaches PIR | CM team |
| Closed or rejected | Requester, with the CM team copied |

The person who did the action is not notified about it. Comments notify nobody.

## Settings

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Required unless `DJANGO_DEBUG=1` |
| `DJANGO_DEBUG` | `1` for local work only |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names the app answers to |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database connection. Leave `POSTGRES_HOST` unset to use SQLite |
| `OIDC_RP_CLIENT_ID`, `OIDC_RP_CLIENT_SECRET` | The portal's client at the sign-on provider. Setting the ID switches single sign-on on |
| `OIDC_OP_AUTHORIZATION_ENDPOINT`, `OIDC_OP_TOKEN_ENDPOINT`, `OIDC_OP_USER_ENDPOINT`, `OIDC_OP_JWKS_ENDPOINT` | The provider's addresses. Required with single sign-on |
| `OIDC_RP_SIGN_ALGO`, `OIDC_RP_SCOPES` | Defaults: `RS256` and `openid email profile` |
| `PORTAL_OIDC_USERNAME_CLAIM`, `PORTAL_OIDC_GROUPS_CLAIM` | Defaults: `preferred_username` and `groups` |
| `PORTAL_OIDC_ROLE_GROUPS` | Optional. Roles from provider groups, e.g. `cm=change-managers,trb=trb-members`. Role names: `cm`, `trb`, `cab`, `authority`, `sw_manager`, `hw_manager` |
| `PORTAL_LOCAL_LOGIN` | `0` hides user-name-and-password sign-in once single sign-on works. Default `1` |
| `EMAIL_HOST`, `EMAIL_PORT` | Mail relay. Setting the host switches email on. Port defaults to `25` |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Only if the relay needs them |
| `PORTAL_EMAIL_FROM` | The From address on emails |
| `PORTAL_BASE_URL` | The portal's address, e.g. `https://changes.example`, for links in emails |
| `PORTAL_MAX_UPLOAD_MB` | Largest single attachment. Default `25` |
| `PORTAL_TIME_ZONE` | Time zone for dates and the yearly CR number reset. Default `UTC` |
