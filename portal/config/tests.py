from unittest import mock

from django.test import TestCase, override_settings

from config import health


class HealthTests(TestCase):
    def test_healthz_needs_no_sign_in(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)

    @override_settings(ALLOWED_HOSTS=["changes.example"], SECURE_SSL_REDIRECT=True)
    def test_probes_work_by_pod_address_over_plain_http(self):
        # The kubelet calls the pod's IP address over HTTP.
        for path in ("/healthz", "/readyz"):
            response = self.client.get(path, HTTP_HOST="10.1.2.3:8000")
            self.assertEqual(response.status_code, 200, path)

    def test_readyz_fails_when_database_is_down(self):
        with mock.patch.object(health, "database_ready", side_effect=Exception("down")):
            response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 503)

    def test_readyz_fails_until_migrations_are_applied(self):
        with mock.patch.object(health, "_migrated", False), mock.patch.object(
            health.MigrationExecutor, "migration_plan", return_value=[("pending", False)]
        ):
            response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 503)
