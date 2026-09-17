import unittest
from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_index_route(self):
        """Test home endpoint renders successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Enterprise EKS GitOps CI/CD", response.data)

    def test_healthz_liveness(self):
        """Test liveness probe endpoint."""
        response = self.client.get('/healthz')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("uptime", data)

    def test_readyz_readiness(self):
        """Test readiness probe endpoint."""
        response = self.client.get('/readyz')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ready")

    def test_metrics_endpoint(self):
        """Test prometheus metrics scraping endpoint."""
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"http_requests_total", response.data)


if __name__ == '__main__':
    unittest.main()
