"""Health checks for the cluster's probes.

/healthz says the process is up. /readyz also checks the database can be
reached and every migration has been applied, so a pod gets no traffic until
the migration Job has finished.
"""
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpResponse

_migrated = False


def database_ready():
    global _migrated
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    if not _migrated:
        executor = MigrationExecutor(connection)
        _migrated = not executor.migration_plan(executor.loader.graph.leaf_nodes())
    return _migrated


class HealthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/healthz":
            return HttpResponse("ok", content_type="text/plain")
        if request.path == "/readyz":
            try:
                ready = database_ready()
            except Exception:
                ready = False
            if ready:
                return HttpResponse("ok", content_type="text/plain")
            return HttpResponse("not ready", status=503, content_type="text/plain")
        return self.get_response(request)
