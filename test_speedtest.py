import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import speedtest

PAYLOAD = b"x" * 500_000


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/missing":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.end_headers()
        self.wfile.write(PAYLOAD)

    def log_message(self, *args):
        pass


class SpeedtestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_fetch_reads_whole_body(self):
        size, seconds = speedtest.fetch(self.base + "/", 5)
        self.assertEqual(size, len(PAYLOAD))
        self.assertGreater(seconds, 0)

    def test_run_makes_all_requests(self):
        results, failed = speedtest.run(self.base + "/", 10, 5)
        self.assertEqual(len(results), 10)
        self.assertEqual(failed, 0)

    def test_failed_requests_are_counted(self):
        results, failed = speedtest.run(self.base + "/missing", 3, 5)
        self.assertEqual(results, [])
        self.assertEqual(failed, 3)

    def test_summarize(self):
        average, total, mbps = speedtest.summarize([(1_000_000, 1.0), (1_000_000, 3.0)])
        self.assertEqual(average, 2.0)
        self.assertEqual(total, 2_000_000)
        self.assertAlmostEqual(mbps, 4.0)  # 16 Mbit in 4 s

    def test_main_exit_codes(self):
        self.assertEqual(speedtest.main([self.base + "/", "-n", "2"]), 0)
        self.assertEqual(speedtest.main([self.base + "/missing", "-n", "2"]), 1)


if __name__ == "__main__":
    unittest.main()
