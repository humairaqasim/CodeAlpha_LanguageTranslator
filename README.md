# Lingua Desk - CodeAlpha Language Translation Tool

Task 1 of the CodeAlpha Artificial Intelligence internship. A Python desktop application that translates text through the MyMemory public REST API. MyMemory is an alternative translation provider to the Google/Microsoft examples in the brief; this project does not use those providers.

## Run on Windows
1. Extract the ZIP.
2. Open the CodeAlpha_LanguageTranslator folder containing app.py and translator.py.
3. Type cmd in File Explorer's address bar and press Enter.
4. Run:

```
py app.py
```

Alternatively, double-click START_WINDOWS.bat. No pip installation is needed. Use Python 3.12 or newer with Tkinter installed (the usual Windows Python installer includes it). On Linux, you may need your distribution's python3-tk package.

## Use the app
1. Select the correct source language and a target language.
2. Enter a short sentence, such as: Hello, how are you?
3. Click Translate (or press Ctrl+Enter).
4. Copy the translation, save it as a UTF-8 text file, or swap the languages.
5. Click History, then search and click a recent translation to restore it without making another request. Repeating the same text and language pair also uses the session cache (up to 100 entries).

Internet access is required for translation. The default source is English and the default target is Urdu. Source-language detection is not implemented; choose the source yourself. Roman Urdu is not equivalent to Urdu script and may produce poor results.

## Features
- Redesigned input and output cards with a light/dark theme switch.
- Adjustable text size with A- and A+ controls.
- Quick presets for English/Urdu and English/Simplified Chinese.
- Import short UTF-8 .txt files (Ctrl+O), translate with Ctrl+Enter, save with Ctrl+S.
- Session translation cache to avoid duplicate API requests; Clear history clears the cache too.
- 14 selectable languages: English, Urdu, Simplified Chinese, Arabic, French, German, Spanish, Hindi, Turkish, Italian, Japanese, Korean, Portuguese and Bengali.
- Source and target selection; reverse translation by swapping languages.
- Character and UTF-8 byte counter.
- Copy translation and save original plus translation.
- Searchable history of the last 50 successful translations, stored in memory for the current session.
- Background network request so the interface remains responsive.
- Clear errors for network failures, malformed responses, quota problems and invalid input.
- Right-aligned Urdu and Arabic output. Script shaping and mixed-script rendering depend on the installed font and Tk version.

## Provider and limits
The app uses https://api.mymemory.translated.net/get with q, langpair and mt=1 parameters. It reads responseData.translatedText after checking responseStatus and quotaFinished.
MyMemory public search does not require an API key. The service documents a maximum of 500 UTF-8 bytes per request and an anonymous usage limit of 5,000 characters per day. Limits and service availability may change; see the official documentation below. The daily quota is managed by the provider, not by this app. No text is silently truncated or split.
Urdu and Chinese characters need multiple bytes, so fewer characters fit within one request. Translation quality and language-pair availability depend on the provider.
The text is sent to MyMemory when Translate is clicked. The app does not contribute translations using the service's set endpoint. History is held only in memory and disappears when the app closes. Saving a result writes a file only when the user chooses to do so.

## Project files
- app.py: Tkinter interface, background worker, clipboard, history and file export.
- translator.py: language codes, validation, API request, response parsing and errors.
- test_translator.py: isolated request/response tests with mocked network responses.
- requirements.txt: explains that no third-party packages are needed.
- START_WINDOWS.bat: Windows launcher.
- .gitignore: excludes Python caches and local virtual environments.

## Tests
```
py -m unittest -v
```
The automated tests check request construction, Unicode decoding, validation, same-language behaviour, quota errors, HTTP errors, offline handling and invalid responses. Additional state tests verify duplicate-request caching, bounded history/cache, clearing history and blocking stale results after edits. Mocked tests do not prove live provider availability or translation accuracy. Test the real interface and an actual translation on your computer before recording your demonstration.

## Beginner explanation
The app is the interface around an existing translation service. It does not train its own AI model. Python sends the text and language codes to an API, receives a JSON response, extracts the translation and displays it. Tkinter builds the window. urllib makes the network request. json reads the response. threading performs the request in the background, and queue passes the result safely back to the interface.

An API is a way for one program to request a service from another. JSON is a structured text format used to carry data. UTF-8 is an encoding that represents characters as bytes.

## Demo video plan
1. Introduce Lingua Desk as CodeAlpha AI Task 1.
2. Select English to Urdu and translate Hello, how are you?
3. Translate a short English sentence into Simplified Chinese.
4. Show Copy result and Save result.
5. Show Swap languages and translate again.
6. Restore an item from recent translations.
7. Explain that Python calls an online API; no model is trained locally.
8. Show the GitHub repository.

## GitHub and submission
Create a repository named CodeAlpha_LanguageTranslator. Upload source files from this folder, including README.md and .gitignore, but exclude the ZIP and __pycache__ folder. Record your own video explaining and demonstrating the working project. Include the repository link in the LinkedIn post, tag CodeAlpha, and submit using the form shared in the internship group.

## Official references
- API specification: https://mymemory.translated.net/doc/spec.php
- Usage limits: https://mymemory.translated.net/doc/usagelimits.php
- Public search key information: https://mymemory.translated.net/doc/keygen.php

## Upgrading from the first version
Extract the updated ZIP into a new folder and run py app.py there. No package installation is needed. The API request limit remains 500 UTF-8 bytes. Live translation was verified for the original API client; the same client is used in this upgrade. Eight automated tests pass. The upgraded desktop layout still requires a visual check on your computer.
