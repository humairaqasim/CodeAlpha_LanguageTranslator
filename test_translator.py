import io
import json
import unittest
from unittest.mock import patch
from urllib.error import URLError, HTTPError
from translator import translate, TranslationError

class APITests(unittest.TestCase):
    def response(self, data):
        return io.BytesIO(json.dumps(data).encode('utf-8'))

    @patch('translator.urlopen')
    def test_request_and_unicode_response(self, call):
        call.return_value = self.response({'responseStatus': 200, 'responseData': {'translatedText': 'سلام &amp; hello'}})
        self.assertEqual(translate('Hello?', 'en', 'ur'), 'سلام & hello')
        request = call.call_args.args[0]
        self.assertIn('langpair=en%7Cur', request.full_url)
        self.assertIn('q=Hello%3F', request.full_url)
        self.assertEqual(call.call_args.kwargs['timeout'], 20)

    @patch('translator.urlopen')
    def test_validation_and_same_language(self, call):
        for args in [('', 'en', 'ur'), ('a'*501, 'en', 'ur'), ('ا'*251, 'ur', 'en'), ('hi', 'xxx', 'ur')]:
            with self.subTest(args=args), self.assertRaises(TranslationError):
                translate(*args)
        self.assertEqual(translate(' hello ', 'en', 'en'), 'hello')
        call.assert_not_called()

    @patch('translator.urlopen')
    def test_errors_do_not_become_translations(self, call):
        for data in [{'responseStatus': 429, 'responseDetails': 'Quota reached'}, {'responseStatus': 200, 'quotaFinished': True}, {'responseStatus': 200, 'responseData': {}}, []]:
            call.return_value = self.response(data)
            with self.subTest(data=data), self.assertRaises(TranslationError):
                translate('Hello', 'en', 'ur')
        call.side_effect = URLError('offline')
        with self.assertRaises(TranslationError):
            translate('Hello', 'en', 'ur')
        call.side_effect = HTTPError('https://example.invalid', 429, 'Rate limit', {}, None)
        with self.assertRaises(TranslationError):
            translate('Hello', 'en', 'ur')

    @patch('translator.urlopen')
    def test_invalid_json(self, call):
        call.return_value = io.BytesIO(b'not JSON')
        with self.assertRaises(TranslationError):
            translate('Hello', 'en', 'ur')

if __name__ == '__main__':
    unittest.main()
