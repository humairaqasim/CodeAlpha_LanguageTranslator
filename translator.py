"""MyMemory public REST API client using Python's standard library."""
import html
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

LANGUAGES = {'English': 'en', 'Urdu': 'ur', 'Chinese (Simplified)': 'zh-CN', 'Arabic': 'ar', 'French': 'fr', 'German': 'de', 'Spanish': 'es', 'Hindi': 'hi', 'Turkish': 'tr', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko', 'Portuguese': 'pt', 'Bengali': 'bn'}
MAX_BYTES = 500

class TranslationError(Exception):
    """A user-readable validation or service error."""

def translate(text, source, target):
    text = text.strip()
    if not text:
        raise TranslationError('Please enter some text to translate.')
    if source not in LANGUAGES.values() or target not in LANGUAGES.values():
        raise TranslationError('Please select supported source and target languages.')
    if len(text.encode('utf-8')) > MAX_BYTES:
        raise TranslationError('This API accepts up to 500 UTF-8 bytes per request. Please shorten the text. Urdu and Chinese letters use more than one byte each.')
    if source == target:
        return text
    url = 'https://api.mymemory.translated.net/get?' + urlencode({'q': text, 'langpair': source + '|' + target, 'mt': '1'})
    request = Request(url, headers={'User-Agent': 'CodeAlpha-LanguageTranslator/1.0', 'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        if error.code == 429:
            raise TranslationError('The service rate limit was reached. Please try again later.') from None
        raise TranslationError(f'The translation service returned HTTP {error.code}. Please try again later.') from None
    except (URLError, TimeoutError, OSError):
        raise TranslationError('Could not reach the translation service. Check your internet connection and try again.') from None
    except (ValueError, UnicodeError):
        raise TranslationError('The service returned an unreadable response. Please try again.') from None
    if not isinstance(data, dict):
        raise TranslationError('The service returned an unexpected response.')
    if data.get('quotaFinished') or str(data.get('responseStatus', '')) != '200':
        detail = str(data.get('responseDetails') or 'Service unavailable or daily translation limit reached.')
        raise TranslationError(detail[:300])
    payload = data.get('responseData')
    answer = payload.get('translatedText') if isinstance(payload, dict) else None
    if not isinstance(answer, str) or not answer.strip():
        raise TranslationError('No translation was returned for this language pair.')
    if answer.upper().startswith('MYMEMORY WARNING:'):
        raise TranslationError('The daily free translation limit has been reached. Please try again later.')
    return html.unescape(answer)
