import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from server import Handler


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request(method, path, body=body, headers=headers or {})
            response = conn.getresponse()
            return response.status, response.read()
        finally:
            conn.close()

    def post_json(self, payload):
        return self.request(
            "POST",
            "/api/calculate",
            body=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

    def test_calculate_ok(self):
        status, body = self.post_json({"expression": "2+3*4"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"result": "14"})

    def test_calculate_error(self):
        status, body = self.post_json({"expression": "1/0"})
        self.assertEqual(status, 422)
        self.assertIn("error", json.loads(body))

    def test_bad_payloads(self):
        for payload in ({}, {"expression": 5}, [1, 2]):
            with self.subTest(payload=payload):
                status, _ = self.post_json(payload)
                self.assertIn(status, (400, 422))

    def test_invalid_json(self):
        status, _ = self.request("POST", "/api/calculate", body="not json")
        self.assertEqual(status, 400)

    def test_unknown_post_path(self):
        status, _ = self.request("POST", "/nope", body="{}")
        self.assertEqual(status, 404)

    def test_serves_front_end(self):
        status, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Calculator", body)
        for asset in ("/style.css", "/app.js"):
            self.assertEqual(self.request("GET", asset)[0], 200)

    def test_no_path_traversal(self):
        status, _ = self.request("GET", "/../calculator.py")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
