import threading
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from ai import ask_ai
from loader import list_files, filter_by_suffix, read_document, read_document_pages
from search import search_term_in_files
from embeddings import get_cached_index, find_relevant_chunks, chunk_label
from prompts import summary_prompt, qa_prompt, strip_markdown
from errors import OllamaError

BG = "#1b1b1f"
BG_SIDEBAR = "#1f2024"
BG_PANEL = "#26262d"
BG_INPUT = "#2c2c34"
FG = "#e8e8ea"
FG_MUTED = "#9a9aa4"
ACCENT = "#8b5cf6"
ACCENT_DIM = "#6d28d9"
USER_BUBBLE = ACCENT
AI_BUBBLE = "#2c2c34"
BORDER = "#34343d"

UI_FONT = ("Bahnschrift SemiBold", 11)
UI_FONT_BOLD = ("Bahnschrift SemiBold", 11, "bold")
TITLE_FONT = ("Bahnschrift SemiBold", 15, "bold")
SUBTITLE_FONT = ("Bahnschrift SemiBold", 10)
TEXT_FONT = ("Cascadia Code", 10)
CHAT_FONT = ("Bahnschrift SemiBold", 11)

NAV_ITEMS = ["Dokumenty", "Vyhladat", "Zhrnut", "Otazky"]

NAV_LABELS = {
    "Dokumenty": "Dokumenty",
    "Vyhladat": "Vyhľadať",
    "Zhrnut": "Zhrnúť",
    "Otazky": "Otázky",
}

SUGGESTED_QUESTIONS = [
    "Čo je umelá inteligencia?",
    "Aký je význam AI pre zdravotníctvo?",
    "Prečo je všeobecná inteligencia pre stroje nedosiahnuteľná?",
]


def get_document_files():
    return filter_by_suffix(list_files())


def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def make_bubble(parent, text, bg, fg, font=CHAT_FONT, max_width=480, radius=16):
    container = tk.Frame(parent, bg=parent["bg"])
    canvas = tk.Canvas(container, bg=parent["bg"], highlightthickness=0, bd=0)
    canvas.pack()

    label = tk.Label(
        canvas, text=text, bg=bg, fg=fg, font=font, justify="left",
        wraplength=max_width, padx=14, pady=10
    )
    window_id = canvas.create_window(0, 0, window=label, anchor="nw")

    def redraw():
        canvas.update_idletasks()
        w = label.winfo_reqwidth()
        h = label.winfo_reqheight()
        canvas.config(width=w, height=h)
        canvas.delete("bg")
        draw_rounded_rect(canvas, 1, 1, w - 1, h - 1, radius, fill=bg, outline=bg, tags="bg")
        canvas.tag_lower("bg")
        canvas.coords(window_id, 0, 0)

    container.after(10, redraw)

    return container


def make_pill_button(parent, text, command, fill=ACCENT, fg="white", font=UI_FONT_BOLD, radius=18):
    container = tk.Frame(parent, bg=parent["bg"])
    canvas = tk.Canvas(container, bg=parent["bg"], highlightthickness=0, cursor="hand2")
    canvas.pack()

    label = tk.Label(canvas, text=text, bg=fill, fg=fg, font=font, padx=22, pady=10, cursor="hand2")
    window_id = canvas.create_window(0, 0, window=label, anchor="nw")

    def redraw():
        canvas.update_idletasks()
        w = label.winfo_reqwidth()
        h = label.winfo_reqheight()
        canvas.config(width=w, height=h)
        canvas.delete("bg")
        draw_rounded_rect(canvas, 1, 1, w - 1, h - 1, radius, fill=fill, outline=fill, tags="bg")
        canvas.tag_lower("bg")
        canvas.coords(window_id, 0, 0)

    container.after(10, redraw)
    canvas.bind("<Button-1>", lambda _e: command())
    label.bind("<Button-1>", lambda _e: command())

    return container


def make_rounded_entry(parent, height=46, radius=20, fill=BG_INPUT):
    container = tk.Frame(parent, bg=parent["bg"])
    canvas = tk.Canvas(container, bg=parent["bg"], highlightthickness=0, height=height)
    canvas.pack(fill="x", expand=True)

    entry = tk.Entry(
        canvas, bg=fill, fg=FG, insertbackground=FG, relief="flat",
        font=UI_FONT, bd=0, highlightthickness=0
    )
    window_id = canvas.create_window(16, height // 2, anchor="w", window=entry)

    def redraw(_event=None):
        w = canvas.winfo_width()

        if w <= 1:
            return

        canvas.delete("bg")
        draw_rounded_rect(canvas, 2, 2, w - 2, height - 2, radius, fill=fill, outline=fill, tags="bg")
        canvas.tag_lower("bg")
        canvas.coords(window_id, 16, height // 2)
        canvas.itemconfig(window_id, width=w - 32)

    canvas.bind("<Configure>", redraw)

    return container, entry


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BP Agent")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG)

        self._apply_theme()

        self.chat_messages = []
        self.ask_sending = False

        self._build_layout()

    # --- theme ---

    def _apply_theme(self):
        global UI_FONT, UI_FONT_BOLD, TEXT_FONT, TITLE_FONT, SUBTITLE_FONT, CHAT_FONT

        available_fonts = set(tkfont.families())

        if "Bahnschrift SemiBold" not in available_fonts:
            UI_FONT = ("Segoe UI", 11) if "Segoe UI" in available_fonts else ("TkDefaultFont", 11)
            UI_FONT_BOLD = (UI_FONT[0], 11, "bold")
            TITLE_FONT = (UI_FONT[0], 15, "bold")
            SUBTITLE_FONT = (UI_FONT[0], 10)
            CHAT_FONT = (UI_FONT[0], 11)

        if "Cascadia Code" not in available_fonts:
            TEXT_FONT = ("Consolas", 10) if "Consolas" in available_fonts else ("TkFixedFont", 10)

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".", background=BG, foreground=FG, font=UI_FONT)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG, font=UI_FONT)
        style.configure(
            "TButton", background=BG_INPUT, foreground=FG, font=UI_FONT,
            padding=6, borderwidth=0, focusthickness=0
        )
        style.map(
            "TButton",
            background=[("active", ACCENT_DIM), ("disabled", BG_PANEL)],
            foreground=[("disabled", FG_MUTED)]
        )
        style.configure(
            "TEntry", fieldbackground=BG_INPUT, foreground=FG, insertcolor=FG,
            borderwidth=1, padding=6
        )

    def _style_listbox(self, listbox):
        listbox.configure(
            bg=BG_INPUT, fg=FG, font=UI_FONT,
            selectbackground=ACCENT, selectforeground="white",
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, borderwidth=0
        )

    def _style_text(self, text_widget):
        text_widget.configure(
            bg=BG_INPUT, fg=FG, font=TEXT_FONT,
            insertbackground=FG, selectbackground=ACCENT, selectforeground="white",
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, borderwidth=0, padx=10, pady=10
        )

        if hasattr(text_widget, "vbar"):
            text_widget.vbar.configure(
                bg=BG_PANEL, activebackground=ACCENT, troughcolor=BG,
                borderwidth=0, highlightthickness=0
            )

    # --- layout ---

    def _build_layout(self):
        root_frame = tk.Frame(self.root, bg=BG)
        root_frame.pack(fill="both", expand=True)

        self._build_sidebar(root_frame)

        content_outer = tk.Frame(root_frame, bg=BG)
        content_outer.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(content_outer, bg=BG)
        self.content.pack(fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.pages["Dokumenty"] = self._build_documents_page(self.content)
        self.pages["Vyhladat"] = self._build_search_page(self.content)
        self.pages["Zhrnut"] = self._build_summary_page(self.content)
        self.pages["Otazky"] = self._build_chat_page(self.content)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.status_var = tk.StringVar(value="Pripravené.")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var, anchor="w",
            padx=14, pady=6, bg=BG_PANEL, fg=FG_MUTED, font=SUBTITLE_FONT
        )
        status_bar.pack(fill="x", side="bottom")

        self._select_nav("Dokumenty")

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=BG_SIDEBAR, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        title = tk.Label(
            sidebar, text="BP Agent", bg=BG_SIDEBAR, fg=FG, font=TITLE_FONT,
            anchor="w", padx=18, pady=22
        )
        title.pack(fill="x")

        self.nav_labels = {}

        for item in NAV_ITEMS:
            label = tk.Label(
                sidebar, text=NAV_LABELS[item], bg=BG_SIDEBAR, fg=FG_MUTED, font=UI_FONT,
                anchor="w", padx=18, pady=12, cursor="hand2"
            )
            label.pack(fill="x")
            label.bind("<Button-1>", lambda _e, name=item: self._select_nav(name))
            label.bind("<Enter>", lambda _e, lbl=label, name=item: self._on_nav_hover(lbl, name, True))
            label.bind("<Leave>", lambda _e, lbl=label, name=item: self._on_nav_hover(lbl, name, False))
            self.nav_labels[item] = label

    def _on_nav_hover(self, label, name, hovering):
        if name == self.current_nav:
            return

        label.configure(bg=BG_PANEL if hovering else BG_SIDEBAR)

    def _select_nav(self, name):
        self.current_nav = name

        for item, label in self.nav_labels.items():
            if item == name:
                label.configure(bg=BG_PANEL, fg=ACCENT, font=UI_FONT_BOLD)
            else:
                label.configure(bg=BG_SIDEBAR, fg=FG_MUTED, font=UI_FONT)

        self.pages[name].tkraise()

    def _page_header(self, parent, title, subtitle=None):
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x", padx=24, pady=(22, 12))

        tk.Label(header, text=title, bg=BG, fg=FG, font=TITLE_FONT, anchor="w").pack(anchor="w")

        if subtitle:
            tk.Label(header, text=subtitle, bg=BG, fg=FG_MUTED, font=SUBTITLE_FONT, anchor="w").pack(anchor="w")

    def set_status(self, text):
        self.status_var.set(text)

    def run_async(self, work, on_done):
        def runner():
            try:
                result = work()
                error = None
            except Exception as exc:
                result = None
                error = exc

            self.root.after(0, lambda: on_done(result, error))

        threading.Thread(target=runner, daemon=True).start()

    def _error_message(self, error):
        if isinstance(error, OllamaError):
            return str(error)

        return f"Nastala neočakávaná chyba: {error}"

    def run(self):
        self.root.mainloop()

    # --- Dokumenty ---

    def _build_documents_page(self, parent):
        page = tk.Frame(parent, bg=BG)
        self._page_header(page, "Dokumenty", "Prehliadaj obsah vložených dokumentov")

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 12))

        ttk.Button(left, text="Obnoviť zoznam", command=self._refresh_documents).pack(fill="x", pady=(0, 6))

        self.documents_listbox = tk.Listbox(left, width=30, exportselection=False)
        self.documents_listbox.pack(fill="y", expand=True)
        self.documents_listbox.bind("<<ListboxSelect>>", self._on_document_selected)
        self._style_listbox(self.documents_listbox)

        self.documents_text = tk.Text(body, wrap="word")
        self.documents_text.pack(side="right", fill="both", expand=True)
        self._style_text(self.documents_text)

        self._refresh_documents()

        return page

    def _refresh_documents(self):
        self.documents_listbox.delete(0, "end")

        for file in get_document_files():
            self.documents_listbox.insert("end", file.name)

    def _on_document_selected(self, _event):
        selection = self.documents_listbox.curselection()

        if not selection:
            return

        file_name = self.documents_listbox.get(selection[0])
        file = next((f for f in get_document_files() if f.name == file_name), None)

        if file is None:
            return

        content = read_document(file)

        self.documents_text.delete("1.0", "end")
        self.documents_text.insert("1.0", content if content is not None else "Tento typ súboru zatiaľ nevieme zobraziť.")

    # --- Vyhladat ---

    def _build_search_page(self, parent):
        page = tk.Frame(parent, bg=BG)
        self._page_header(page, "Vyhľadať", "Nájdi presný výraz vo vložených dokumentoch")

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        top = tk.Frame(body, bg=BG)
        top.pack(fill="x", pady=(0, 10))

        self.search_entry = ttk.Entry(top)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda _event: self._run_search())

        ttk.Button(top, text="Vyhľadať", command=self._run_search).pack(side="left", padx=(8, 0))

        self.search_text = tk.Text(body, wrap="word")
        self.search_text.pack(fill="both", expand=True)
        self._style_text(self.search_text)

        return page

    def _run_search(self):
        term = self.search_entry.get().strip()
        self.search_text.delete("1.0", "end")

        if not term:
            return

        matches = search_term_in_files(get_document_files(), term)

        if not matches:
            self.search_text.insert("end", "Výraz sa nenašiel v žiadnom dokumente.")
            return

        for match in matches:
            self.search_text.insert("end", f"[{match['file']}, riadok {match['line_number']}]\n{match['text']}\n\n")

    # --- Zhrnut ---

    def _build_summary_page(self, parent):
        page = tk.Frame(parent, bg=BG)
        self._page_header(page, "Zhrnúť", "Vyber dokument a vygeneruj jeho zhrnutie")

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 12))

        ttk.Button(left, text="Obnovit zoznam", command=self._refresh_summary_documents).pack(fill="x", pady=(0, 6))

        self.summary_listbox = tk.Listbox(left, width=30, exportselection=False)
        self.summary_listbox.pack(fill="y", expand=True)
        self._style_listbox(self.summary_listbox)

        self.summary_button = ttk.Button(left, text="Zhrnúť dokument", command=self._run_summary)
        self.summary_button.pack(fill="x", pady=(6, 0))

        self.summary_text = tk.Text(body, wrap="word")
        self.summary_text.pack(side="right", fill="both", expand=True)
        self._style_text(self.summary_text)

        self._refresh_summary_documents()

        return page

    def _refresh_summary_documents(self):
        self.summary_listbox.delete(0, "end")

        for file in get_document_files():
            self.summary_listbox.insert("end", file.name)

    def _run_summary(self):
        selection = self.summary_listbox.curselection()

        if not selection:
            self.set_status("Najprv vyber dokument.")
            return

        file_name = self.summary_listbox.get(selection[0])
        file = next((f for f in get_document_files() if f.name == file_name), None)

        if file is None:
            return

        content = read_document(file)

        if not content or not content.strip():
            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("1.0", "Dokument je prázdny alebo sa nepodarilo načítať text.")
            return

        self.summary_button.config(state="disabled")
        self.summary_text.delete("1.0", "end")
        self.set_status("Generujem zhrnutie...")

        self.run_async(
            lambda: strip_markdown(ask_ai(summary_prompt(content))),
            self._on_summary_done
        )

    def _on_summary_done(self, result, error):
        self.summary_button.config(state="normal")

        if error is not None:
            self.summary_text.insert("1.0", self._error_message(error))
            self.set_status("Nastala chyba.")
            return

        self.summary_text.insert("1.0", result)
        self.set_status("Hotovo.")

    # --- Otazky (chat) ---

    def _build_chat_page(self, parent):
        page = tk.Frame(parent, bg=BG)
        self._page_header(page, "Otázky", "Spýtaj sa na obsah vložených dokumentov")

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self.chat_canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        self.chat_scrollbar = tk.Scrollbar(body, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.chat_scrollbar.pack(side="right", fill="y")

        self.chat_messages_frame = tk.Frame(self.chat_canvas, bg=BG)
        self.chat_window_id = self.chat_canvas.create_window((0, 0), window=self.chat_messages_frame, anchor="nw")

        self.chat_messages_frame.bind(
            "<Configure>",
            lambda _e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        self.chat_canvas.bind(
            "<Configure>",
            lambda e: self.chat_canvas.itemconfig(self.chat_window_id, width=e.width)
        )
        self.chat_canvas.bind("<MouseWheel>", lambda e: self.chat_canvas.yview_scroll(int(-e.delta / 40), "units"))

        self._render_suggestions()

        input_bar = tk.Frame(page, bg=BG)
        input_bar.pack(fill="x", padx=24, pady=(0, 20))

        entry_pill, self.ask_entry = make_rounded_entry(input_bar)
        entry_pill.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ask_entry.bind("<Return>", lambda _event: self._send_question())

        send_pill = make_pill_button(input_bar, "Odoslať", self._send_question)
        send_pill.pack(side="left")

        return page

    def _render_suggestions(self):
        suggestions_frame = tk.Frame(self.chat_messages_frame, bg=BG)
        suggestions_frame.pack(fill="x", pady=(10, 4))

        tk.Label(
            suggestions_frame, text="Skús napríklad:", bg=BG, fg=FG_MUTED, font=SUBTITLE_FONT
        ).pack(anchor="w", pady=(0, 6))

        for question in SUGGESTED_QUESTIONS:
            chip = make_bubble(suggestions_frame, question, bg=BG_PANEL, fg=FG_MUTED, font=SUBTITLE_FONT, max_width=600)
            chip.pack(anchor="w", pady=3)
            self._bind_chip_click(chip, question)

        self.suggestions_frame = suggestions_frame

    def _bind_chip_click(self, widget, question):
        widget.bind("<Button-1>", lambda _e: self._use_suggestion(question))

        for child in widget.winfo_children():
            child.configure(cursor="hand2")
            child.bind("<Button-1>", lambda _e: self._use_suggestion(question))

    def _use_suggestion(self, question):
        self.ask_entry.delete(0, "end")
        self.ask_entry.insert(0, question)
        self._send_question()

    def _scroll_chat_to_bottom(self):
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _add_user_message(self, text):
        if self.suggestions_frame is not None:
            self.suggestions_frame.destroy()
            self.suggestions_frame = None

        row = tk.Frame(self.chat_messages_frame, bg=BG)
        row.pack(fill="x", pady=4)

        bubble = make_bubble(row, text, bg=USER_BUBBLE, fg="white", font=CHAT_FONT)
        bubble.pack(side="right", padx=(80, 0))

        self._scroll_chat_to_bottom()

    def _add_ai_message(self, text, sources_text=None):
        row = tk.Frame(self.chat_messages_frame, bg=BG)
        row.pack(fill="x", pady=4)

        bubble = make_bubble(row, text, bg=AI_BUBBLE, fg=FG, font=CHAT_FONT)
        bubble.pack(side="left", padx=(0, 80))

        if sources_text:
            sources_row = tk.Frame(self.chat_messages_frame, bg=BG)
            sources_row.pack(fill="x", pady=(0, 6))

            sources_bubble = make_bubble(
                sources_row, sources_text, bg=BG, fg=FG_MUTED, font=SUBTITLE_FONT, max_width=520
            )
            sources_bubble.pack(side="left", padx=(0, 80))

        self._scroll_chat_to_bottom()
        return row

    def _send_question(self):
        if self.ask_sending:
            return

        question = self.ask_entry.get().strip()

        if not question:
            return

        self.ask_entry.delete(0, "end")
        self._add_user_message(question)

        placeholder = self._add_ai_message("Premýšľam...")

        self.ask_sending = True
        self.set_status("Indexujem dokumenty...")

        self.run_async(
            lambda: self._answer_question(question),
            lambda result, error: self._on_ask_done(result, error, placeholder)
        )

    def _answer_question(self, question):
        files = get_document_files()
        index, _was_rebuilt = get_cached_index(files, read_document_pages)

        if not index:
            return {"chunks": [], "answer": None}

        relevant_chunks = find_relevant_chunks(index, question)

        if not relevant_chunks:
            return {"chunks": [], "answer": None}

        answer = strip_markdown(ask_ai(qa_prompt(question, relevant_chunks)))

        return {"chunks": relevant_chunks, "answer": answer}

    def _on_ask_done(self, result, error, placeholder):
        placeholder.destroy()
        self.ask_sending = False

        if error is not None:
            self._add_ai_message(self._error_message(error))
            self.set_status("Nastala chyba.")
            return

        if not result["chunks"]:
            self._add_ai_message("Nenašli sa žiadne relevantné pasáže v dokumentoch.")
            self.set_status("Hotovo.")
            return

        unique_labels = list(dict.fromkeys(chunk_label(chunk) for chunk in result["chunks"]))
        sources_text = "Zdroje: " + ", ".join(unique_labels)

        self._add_ai_message(result["answer"], sources_text)
        self.set_status("Hotovo.")


if __name__ == "__main__":
    App().run()
