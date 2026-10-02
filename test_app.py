"""State tests without opening a display or contacting the API."""
import unittest
from unittest.mock import Mock, patch
from app import TranslatorApp

class SessionTests(unittest.TestCase):
    def make_app(self):
        app = TranslatorApp.__new__(TranslatorApp)
        app.busy = False
        app.cache = {}
        app.history = []
        app.snapshot = None
        app.status = Mock()
        app.show_result = Mock()
        app.render_history = Mock()
        return app

    @patch('app.translate')
    def test_repeat_uses_cache_without_network(self, translate):
        app = self.make_app()
        app.current = Mock(return_value=('Hello', 'English', 'Urdu'))
        app.complete('Hello', 'English', 'Urdu', 'سلام')
        app.start()
        translate.assert_not_called()
        self.assertEqual(len(app.history), 1)
        app.show_result.assert_called_with('سلام', 'Urdu')

    def test_changed_input_blocks_copying_old_result(self):
        app = self.make_app()
        app.output = Mock()
        app.output.get.return_value = 'سلام'
        app.snapshot = ('Hello', 'English', 'Urdu')
        app.current = Mock(return_value=('Different text', 'English', 'Urdu'))
        self.assertIsNone(app.valid_result())

    def test_history_and_cache_are_bounded(self):
        app = self.make_app()
        for i in range(110):
            app.complete(str(i), 'English', 'Urdu', str(i))
        self.assertEqual(len(app.history), 50)
        self.assertEqual(len(app.cache), 100)

    def test_clear_history_also_clears_cache(self):
        app = self.make_app()
        app.complete('Hello', 'English', 'Urdu', 'سلام')
        app.clear_history()
        self.assertEqual(app.history, [])
        self.assertEqual(app.cache, {})

if __name__ == '__main__':
    unittest.main()
