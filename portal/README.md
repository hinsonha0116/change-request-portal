# Change Request Portal: standalone version

A Django rebuild of the Power Apps portal, meant to run in a Kubernetes cluster with no Microsoft 365 services. The guides in the parent folder are the specification.

**Status:** all 6 steps are done: the data model, the stage rules, the screens, sign-in and roles, notifications with email, the container image with its Helm chart, and a full run in a local Kubernetes cluster. What is left needs the real cluster's services: the Ingress, single sign-on and the mail relay. See [What has been checked](#what-has-been-checked).

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
| `config/` | Settings, read from environment variables. `settings_dev.py` is for local work only. `health.py` answers the cluster's health probes |
| `Dockerfile` | The container image |
| `deploy/chart/` | The Helm chart: portal, database, migration Job and backups |

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

## Run it in the cluster

Needs Docker to build the image, and Helm 3 with access to the cluster.

Build the image and push it to a registry the cluster can pull from:

```bash
docker build -t <registry>/change-request-portal:0.1.0 .
```

```bash
docker push <registry>/change-request-portal:0.1.0
```

Install it. `host` is the name people will type to reach the portal:

```bash
helm install portal deploy/chart --namespace change-portal --create-namespace --set image.repository=<registry>/change-request-portal --set host=changes.example --set ingress.enabled=true
```

Create the first account, which can then add everyone else on the People screen:

```bash
kubectl -n change-portal exec -it deploy/portal -- python manage.py createsuperuser
```

Every other setting is described in `deploy/chart/values.yaml`. Upgrade with `helm upgrade` and the same settings.

What the chart sets up:

- **The portal**: two pods behind a Service, and an Ingress if `ingress.enabled` is set. The pods run as an unprivileged user with a read-only file system.
- **The database**: one PostgreSQL pod with its own volume. To use a database run elsewhere, set `postgresql.enabled=false` and `externalDatabase.host`.
- **Migrations**: a Job brings the tables up to date on every install and upgrade. Portal pods take no traffic until it has finished.
- **Backups**: a nightly `pg_dump` to a second volume, kept for 14 days. One file holds everything: requests, history, attachments and users.
- **Passwords**: the secret key and database password are generated on first install and kept in a Secret. To supply your own Secret, set `secrets.existingSecret`.

The portal expects HTTPS to end at the Ingress. It redirects plain HTTP, marks its cookies secure, and sends the HSTS header. Attachments can be 25 MB, so the Ingress must allow request bodies that large; `values.yaml` shows the annotation for ingress-nginx.

Restore a backup into an empty database with:

```bash
pg_restore --no-owner -d portal /backups/portal-<date>-<time>.dump
```

### What has been checked

The chart was installed in a local Kubernetes 1.34 cluster (kind), with the chart's default settings: two portal pods, the bundled PostgreSQL 17, and backups on.

- `helm install --wait` finishes in under 30 seconds. The migration Job retries until the database is up, and the portal pods take no traffic until it has finished.
- 30 people submitting at the same moment through the Service, spread over both portal pods, got CR-2026-001 to CR-2026-030, with no repeats and no gaps.
- The backup CronJob writes a dump, and that dump restores into an empty database with every request in it.
- Deleting the database pod loses nothing.
- `helm upgrade` runs a new migration Job, scales the portal, and keeps the generated secret key and database password.
- `helm uninstall` keeps the Secret, the database volume and the backup volume, so installing again brings back all the data.
- The portal pods run as an unprivileged user and cannot write to their file system.
- All 119 tests pass against PostgreSQL, and `manage.py check --deploy` passes.

Not checked yet. These need the real cluster's services:

- **The Ingress.** The template renders, but no Ingress controller has served the portal yet. The test cluster could not download one. Check that HTTPS works and that a 25 MB attachment uploads.
- Single sign-on against a real provider, and email through a real relay.

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
| `PORTAL_HTTPS` | `0` turns off the HTTPS redirect and secure cookies, to try the image over plain HTTP. Default `1` unless `DJANGO_DEBUG=1` |
| `PORTAL_HSTS_SECONDS`, `PORTAL_HSTS_INCLUDE_SUBDOMAINS` | The HSTS header. Defaults: one year, this host only |
| `PORTAL_LOG_LEVEL` | Default `INFO`. Logs go to the console |
| `PORTAL_TIME_ZONE` | Time zone for dates and the yearly CR number reset. Default `UTC` |
