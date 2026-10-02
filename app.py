"""Lingua Desk: run with py app.py. No pip installation required."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
from pathlib import Path
import queue
import threading
from translator import LANGUAGES, MAX_BYTES, translate, TranslationError

BG = '#f1f5f8'
NAVY = '#173b50'
TEAL = '#087e83'

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        self.history = []
        self.cache = {}
        self.snapshot = None
        self.dark = False
        self.font_size = 14
        root.title('Lingua Desk Studio | CodeAlpha AI Task 1')
        root.geometry('1080x760')
        root.minsize(760, 580)
        root.configure(bg=BG)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1, minsize=240)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TCombobox', padding=8, font=('Segoe UI', 10))
        header = tk.Frame(root, bg=NAVY, padx=20, pady=10)
        header.grid(row=0, column=0, sticky='ew')
        branding = tk.Frame(header, bg=NAVY)
        branding.pack(side='left')
        tk.Label(branding, text='Lingua Desk', bg=NAVY, fg='white', font=('Segoe UI', 20, 'bold')).pack(anchor='w')
        tk.Label(branding, text='TRANSLATION STUDIO  /  CODEALPHA AI TASK 1', bg=NAVY, fg='#cbdfe8', font=('Segoe UI', 9)).pack(anchor='w', pady=(3, 0))
        self.theme_button = self.button(header, 'Dark theme', self.toggle_theme)
        self.theme_button.pack(side='right')
        self.button(header, 'Help', self.help).pack(side='right', padx=8)
        tk.Label(root, text='Choose your languages, then type in the box on the left.', bg=BG, fg=NAVY, font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', padx=24, pady=(8, 6))
        toolbar = tk.Frame(root, bg=BG)
        toolbar.grid(row=2, column=0, sticky='ew', padx=24, pady=(0, 6))
        self.source = tk.StringVar(value='English')
        self.target = tk.StringVar(value='Urdu')
        presets = [('English → Urdu', 'English', 'Urdu'), ('English → Chinese', 'English', 'Chinese (Simplified)'), ('Urdu → English', 'Urdu', 'English')]
        for label, source, target in presets:
            self.button(toolbar, label, lambda a=source, b=target: self.preset(a, b)).pack(side='left', padx=(0, 7))
        self.button(toolbar, 'A+', lambda: self.resize_font(1)).pack(side='right', padx=(6, 0))
        self.button(toolbar, 'A−', lambda: self.resize_font(-1)).pack(side='right')
        content = tk.Frame(root, bg=BG)
        content.grid(row=3, column=0, sticky='nsew', padx=24)
        content.columnconfigure(0, weight=1, uniform='cards')
        content.columnconfigure(1, weight=1, uniform='cards')
        content.rowconfigure(0, weight=1)
        self.source_menu = None
        self.target_menu = None
        for column, title, subtitle, variable in [(0, 'Original text', 'Write or import a short message', self.source), (1, 'Translation', 'Your translated result', self.target)]:
            card = tk.Frame(content, bg='white', padx=12, pady=10, highlightbackground='#dbe5ec', highlightthickness=1)
            card.grid(row=0, column=column, sticky='nsew', padx=(0, 8) if column == 0 else (8, 0))
            card.columnconfigure(0, weight=1)
            card.rowconfigure(3, weight=1, minsize=100)
            tk.Label(card, text=title, bg='white', fg=NAVY, font=('Segoe UI', 14, 'bold')).grid(row=0, column=0, sticky='w')
            tk.Label(card, text=subtitle, bg='white', fg='#647b87', font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=(2, 6))
            menu = ttk.Combobox(card, values=list(LANGUAGES), textvariable=variable, state='readonly')
            menu.grid(row=2, column=0, sticky='ew', pady=(0, 6))
            text = ScrolledText(card, wrap='word', width=10, height=4, font=('Segoe UI', self.font_size), relief='solid', borderwidth=1, highlightthickness=1, highlightbackground='#dbe5ec', highlightcolor=TEAL, padx=10, pady=10, undo=column == 0, bg='#f1f5f8', fg=NAVY, insertbackground=TEAL)
            text.grid(row=3, column=0, sticky='nsew')
            footer = tk.Frame(card, bg='white')
            footer.grid(row=4, column=0, sticky='ew', pady=(10, 0))
            if column == 0:
                self.source_menu = menu
                self.input = text
                self.import_button = self.button(footer, 'Import .txt', self.import_text)
                self.import_button.pack(side='left')
                self.clear_button = self.button(footer, 'Clear', self.clear)
                self.clear_button.pack(side='right')
            else:
                self.target_menu = menu
                self.output = text
                self.output.configure(state='disabled')
                self.output.tag_configure('rtl', justify='right')
                self.output.tag_configure('ltr', justify='left')
                self.button(footer, 'Copy', self.copy).pack(side='left')
                self.button(footer, 'Save .txt', self.save).pack(side='right')
        controls = tk.Frame(root, bg=BG)
        controls.grid(row=4, column=0, sticky='ew', padx=24, pady=(10, 0))
        self.counter = tk.StringVar()
        tk.Label(controls, textvariable=self.counter, bg=BG, fg='#647b87', font=('Segoe UI', 9)).pack(side='left')
        self.translate_button = self.button(controls, 'Translate  →', self.start, True)
        self.translate_button.pack(side='right', padx=(10, 0))
        self.button(controls, 'History', self.toggle_history).pack(side='right', padx=(10, 0))
        self.swap_button = self.button(controls, 'Swap languages', self.swap)
        self.swap_button.pack(side='right')
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.grid(row=5, column=0, sticky='ew', padx=24, pady=(10, 0))
        self.status = tk.StringVar(value='Ready • Ctrl+Enter to translate. No API key needed.')
        tk.Label(root, textvariable=self.status, bg=BG, fg=NAVY, anchor='w', wraplength=900, font=('Segoe UI', 9)).grid(row=6, column=0, sticky='ew', padx=24, pady=8)
        self.history_frame = tk.Frame(root, bg=BG)
        self.history_frame.grid(row=7, column=0, sticky='ew', padx=24, pady=(0, 8))
        line = tk.Frame(self.history_frame, bg=BG)
        line.pack(fill='x')
        tk.Label(line, text='RECENT TRANSLATIONS', bg=BG, fg=NAVY, font=('Segoe UI', 9, 'bold')).pack(side='left')
        self.history_search = tk.StringVar()
        ttk.Entry(line, textvariable=self.history_search, width=22).pack(side='left', padx=12)
        self.history_search.trace_add('write', lambda *_: self.render_history())
        self.button(line, 'Clear history', self.clear_history).pack(side='right')
        self.list = tk.Listbox(self.history_frame, height=2, font=('Segoe UI', 9), bg='white', fg=NAVY, borderwidth=0, highlightthickness=0, selectbackground=TEAL, selectforeground='white', exportselection=False)
        self.list.pack(fill='x', pady=(4, 0))
        self.list.bind('<<ListboxSelect>>', self.restore)
        self.filtered_history = []
        tk.Label(root, text='Powered by MyMemory • Text is sent online when translated • History and cache stay in this session', bg=BG, fg='#647b87', font=('Segoe UI', 8)).grid(row=8, column=0, sticky='ew', padx=24, pady=(0, 6))
        self.input.tag_configure('rtl', justify='right')
        self.input.tag_configure('ltr', justify='left')
        self.input.bind('<<Modified>>', self.changed)
        self.source_menu.bind('<<ComboboxSelected>>', lambda e: self.invalidate())
        self.target_menu.bind('<<ComboboxSelected>>', lambda e: self.invalidate())
        root.bind('<Control-Return>', lambda e: self.start())
        root.bind('<Control-s>', lambda e: self.save())
        root.bind('<Control-o>', lambda e: self.import_text())
        self.history_frame.grid_remove()
        self.history_visible = False
        self.count()
        root.after(100, self.poll)
        self.input.focus_set()

    def button(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, bg=TEAL if primary else 'white', fg='white' if primary else NAVY, activebackground='#d8ebed', relief='flat', padx=10, pady=7, font=('Segoe UI', 9, 'bold'), cursor='hand2')

    def current(self):
        return self.input.get('1.0', 'end-1c').strip(), self.source.get(), self.target.get()

    def count(self):
        text = self.input.get('1.0', 'end-1c')
        self.counter.set(f'{len(text)} characters  /  {len(text.strip().encode("utf-8"))} of {MAX_BYTES} bytes')
        self.input.tag_remove('rtl', '1.0', 'end')
        self.input.tag_remove('ltr', '1.0', 'end')
        self.input.tag_add('rtl' if self.source.get() in {'Urdu', 'Arabic'} else 'ltr', '1.0', 'end')

    def changed(self, event=None):
        if self.input.edit_modified():
            self.input.edit_modified(False)
            self.count()
            self.invalidate()

    def invalidate(self):
        self.count()
        if not self.busy and self.snapshot and self.current() != self.snapshot:
            self.status.set('Text or languages changed. Click Translate to update the result.')

    def show_result(self, text, target):
        self.output.configure(state='normal')
        self.output.delete('1.0', 'end')
        self.output.insert('1.0', text, 'rtl' if target in {'Urdu', 'Arabic'} else 'ltr')
        self.output.configure(state='disabled')

    def set_busy(self, busy):
        self.busy = busy
        state = 'disabled' if busy else 'normal'
        for button in (self.translate_button, self.swap_button, self.clear_button, self.import_button):
            button.configure(state=state)
        self.input.configure(state=state)
        self.source_menu.configure(state='disabled' if busy else 'readonly')
        self.target_menu.configure(state='disabled' if busy else 'readonly')
        self.list.configure(state=state)
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def start(self):
        if self.busy:
            return
        text, source, target = self.current()
        if not text:
            self.status.set('Please enter text first.')
            return
        if len(text.encode('utf-8')) > MAX_BYTES:
            self.status.set('Please shorten the text to 500 UTF-8 bytes or fewer.')
            return
        key = (text, source, target)
        if key in self.cache:
            self.complete(text, source, target, self.cache[key])
            self.status.set('Restored from session cache • No API request used.')
            return
        self.show_result('', target)
        self.snapshot = None
        self.set_busy(True)
        self.status.set('Translating… Please wait.')
        def work():
            try:
                answer = translate(text, LANGUAGES[source], LANGUAGES[target])
                self.events.put(('ok', (text, source, target, answer)))
            except TranslationError as error:
                self.events.put(('error', str(error)))
            except Exception:
                self.events.put(('error', 'An unexpected error occurred. Please try again.'))
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            kind, value = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            self.set_busy(False)
            if kind == 'error':
                self.status.set(value)
            else:
                text, source, target, answer = value
                self.complete(text, source, target, answer)
        self.root.after(100, self.poll)

    def valid_result(self):
        answer = self.output.get('1.0', 'end-1c').strip()
        if not answer:
            self.status.set('Translate some text first.')
            return None
        if self.current() != self.snapshot:
            self.status.set('Please translate again after changing the text or languages.')
            return None
        return answer

    def copy(self):
        answer = self.valid_result()
        if answer:
            self.root.clipboard_clear()
            self.root.clipboard_append(answer)
            self.status.set('Translation copied to clipboard.')

    def save(self):
        answer = self.valid_result()
        if not answer:
            return
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension='.txt', initialfile='Translation.txt', filetypes=[('Text file', '*.txt')])
        if path:
            text, source, target = self.snapshot
            content = f'Lingua Desk | {datetime.now():%Y-%m-%d %H:%M}\n{source} → {target}\n\nOriginal:\n{text}\n\nTranslation:\n{answer}\n'
            try:
                Path(path).write_text(content, encoding='utf-8')
            except OSError as error:
                messagebox.showerror('Could not save', str(error), parent=self.root)
            else:
                self.status.set('Translation saved.')

    def swap(self):
        if self.busy:
            return
        answer = self.valid_result() if self.snapshot else None
        source, target = self.source.get(), self.target.get()
        self.source.set(target)
        self.target.set(source)
        if answer:
            self.input.delete('1.0', 'end')
            self.input.insert('1.0', answer)
        self.show_result('', source)
        self.snapshot = None
        self.count()
        self.status.set('Languages swapped • Click Translate for the reverse translation.')

    def clear(self):
        self.input.delete('1.0', 'end')
        self.show_result('', self.target.get())
        self.snapshot = None
        self.count()
        self.status.set('Ready for a new translation.')

    def restore(self, event):
        if self.busy:
            return
        selected = self.list.curselection()
        if not selected:
            return
        item = self.filtered_history[selected[0]]
        self.source.set(item['source'])
        self.target.set(item['target'])
        self.input.delete('1.0', 'end')
        self.input.insert('1.0', item['input'])
        self.snapshot = (item['input'], item['source'], item['target'])
        self.show_result(item['output'], item['target'])
        self.count()
        self.status.set('Previous translation restored.')

    def complete(self, text, source, target, answer):
        self.snapshot = (text, source, target)
        self.show_result(answer, target)
        self.cache[self.snapshot] = answer
        if len(self.cache) > 100:
            del self.cache[next(iter(self.cache))]
        self.history = [item for item in self.history if (item['input'], item['source'], item['target']) != self.snapshot]
        self.history.insert(0, {'input': text, 'source': source, 'target': target, 'output': answer})
        self.history = self.history[:50]
        self.render_history()
        self.status.set('Same language: copied unchanged.' if source == target else 'Translation complete • Check wording before use.')

    def render_history(self):
        query = self.history_search.get().strip().lower()
        self.filtered_history = [item for item in self.history if query in ' '.join(item.values()).lower()]
        self.list.configure(state='normal')
        self.list.delete(0, 'end')
        for item in self.filtered_history:
            preview = item['input'].replace('\n', ' ')[:70]
            self.list.insert('end', f"{item['source']} → {item['target']}   |   {preview}")
        self.list.configure(state='disabled' if self.busy else 'normal')

    def toggle_history(self):
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.history_frame.grid()
        else:
            self.history_frame.grid_remove()

    def clear_history(self):
        if self.busy:
            return
        self.history.clear()
        self.cache.clear()
        self.render_history()
        self.status.set('Session history and cache cleared.')

    def preset(self, source, target):
        if self.busy:
            return
        self.source.set(source)
        self.target.set(target)
        self.invalidate()
        self.input.focus_set()

    def import_text(self):
        if self.busy:
            return
        path = filedialog.askopenfilename(parent=self.root, title='Import a short UTF-8 text file', filetypes=[('Text files', '*.txt')])
        if not path:
            return
        try:
            if Path(path).stat().st_size > 100000:
                raise ValueError('Select a small text file. Maximum import size is 100 KB.')
            text = Path(path).read_text(encoding='utf-8-sig')
            if len(text.strip().encode('utf-8')) > MAX_BYTES:
                raise ValueError('This file exceeds the 500-byte translation limit. Copy a shorter passage instead.')
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror('Cannot import file', str(error), parent=self.root)
            return
        self.input.delete('1.0', 'end')
        self.input.insert('1.0', text)
        self.show_result('', self.target.get())
        self.snapshot = None
        self.count()
        self.status.set('Text imported • Click Translate.')

    def resize_font(self, delta):
        self.font_size = max(10, min(24, self.font_size + delta))
        for widget in (self.input, self.output):
            widget.configure(font=('Segoe UI', self.font_size))

    def toggle_theme(self):
        self.dark = not self.dark
        if not hasattr(self, '_theme_originals'):
            self._theme_originals = []
            def collect(widget):
                values = {option: str(widget.cget(option)) for option in ('bg', 'fg', 'highlightbackground') if option in widget.keys()}
                self._theme_originals.append((widget, values))
                for child in widget.winfo_children():
                    collect(child)
            collect(self.root)
        for widget, original in self._theme_originals:
            adjusted = dict(original)
            if self.dark:
                adjusted['bg'] = {BG: '#101c29', 'white': '#1b2c3e'}.get(original.get('bg'), original.get('bg'))
                if original.get('fg') == NAVY:
                    adjusted['fg'] = '#d9e8f1'
                elif original.get('fg') == '#647b87':
                    adjusted['fg'] = '#9bb0c3'
                adjusted['highlightbackground'] = '#304456' if original.get('highlightbackground') == '#dbe5ec' else original.get('highlightbackground')
            adjusted = {key: value for key, value in adjusted.items() if value is not None}
            widget.configure(**adjusted)
        self.theme_button.configure(text='Light theme' if self.dark else 'Dark theme')
        style = ttk.Style(self.root)
        style.configure('TCombobox', fieldbackground='#1b2c3e' if self.dark else 'white', foreground='#d9e8f1' if self.dark else NAVY, background='#304456' if self.dark else '#dbe5ec')
        style.map('TCombobox', fieldbackground=[('readonly', '#1b2c3e' if self.dark else 'white')], foreground=[('readonly', '#d9e8f1' if self.dark else NAVY)])

    def help(self):
        messagebox.showinfo('Welcome to Lingua Desk', '1. Choose the source and target languages.\n2. Type a sentence or import a short .txt file.\n3. Click Translate.\n\nCtrl+Enter: translate\nCtrl+O: import text\nCtrl+S: save translation\nA− / A+: change text size\n\nSearch recent translations to restore them. Repeated translations use the session cache.\n\nThe public API accepts at most 500 UTF-8 bytes per request. New requests need internet. Urdu/Arabic alignment is supported; font rendering varies by system. This app uses an existing translation service rather than training a model.', parent=self.root)

if __name__ == '__main__':
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()
