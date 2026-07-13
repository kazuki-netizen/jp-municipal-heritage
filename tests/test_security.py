import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "site" / "build_pages.py"
SPEC = importlib.util.spec_from_file_location("build_pages", MODULE_PATH)
build_pages = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_pages)


class SafeUrlTests(unittest.TestCase):
    def test_allows_http_and_https(self):
        self.assertEqual(build_pages.safe_http_url("https://example.jp/a?q=1"),
                         "https://example.jp/a?q=1")
        self.assertEqual(build_pages.safe_http_url("http://example.jp/a"),
                         "http://example.jp/a")

    def test_rejects_active_or_ambiguous_schemes(self):
        for value in (
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "//example.jp/path",
            "/relative/path",
            "https://user:password@example.jp/",
            "not a url",
        ):
            with self.subTest(value=value):
                self.assertEqual(build_pages.safe_http_url(value), "")

    def test_render_does_not_link_dangerous_source(self):
        row = {
            "name": "test",
            "jmh_id": "JMH-000000-0001",
            "source_url": "javascript:alert(1)",
        }
        page = build_pages.render(row, {})
        self.assertNotIn('href="javascript:', page)
        self.assertIn("javascript:alert(1)", page)


if __name__ == "__main__":
    unittest.main()
