from __future__ import annotations
import os
import sys
import threading
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from khaton.bytecode import compile_source, save_bytecode
from khaton.lexer import COMMANDS
from khaton.parser import parse
from khaton.runtime import KhatonRuntime

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

BG = "#101217"
PANEL = "#181c24"
EDITOR = "#0d1117"
TEXT = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
ERROR = "#f85149"
GOLD = "#d6ad66"
GITHUB_URL = "https://github.com/e3e4e5hoi-star/Khaton"
KEYWORDS = set(COMMANDS)

class LineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=48, bg=EDITOR, highlightthickness=0, **kwargs)
        self.text_widget = text_widget
        self.redraw()
    def redraw(self, *_):
        self.delete("all")
        first = int(self.text_widget.index("@0,0").split('.')[0])
        last = int(self.text_widget.index(f"@0,{self.winfo_height()}").split('.')[0]) + 1
        for line in range(first, last + 1):
            y = self.text_widget.dlineinfo(f"{line}.0")
            if y:
                self.create_text(42, y[1] + 2, anchor="ne", text=str(line), fill=MUTED, font=("Consolas", 10))

class KhatonStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Khaton Studio · Khaton Language")
        self.geometry("1180x760")
        self.minsize(860, 560)
        self.configure(bg=BG)
        self.current_file: Path | None = None
        self._build_ui()
        self._load_example()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", background=PANEL, foreground=TEXT, padding=(11, 7), borderwidth=0, font=("Segoe UI", 9))
        style.map("TButton", background=[("active", "#2b3a50")], foreground=[("active", "#ffffff")])
        style.configure("Accent.TButton", background=GOLD, foreground="#15181d", padding=(12, 7), font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton", background=[("active", "#edc57e")])
        header = tk.Frame(self, bg=BG, height=78); header.pack(fill="x", padx=18, pady=(12, 5))
        logo_path = ROOT / "studio" / "assets" / "khaton-camel.jpg"
        if Image and logo_path.exists():
            image = Image.open(logo_path).resize((54, 54))
            self.logo = ImageTk.PhotoImage(image)
            tk.Label(header, image=self.logo, bg=BG).pack(side="left", padx=(0, 12))
        title = tk.Frame(header, bg=BG); title.pack(side="left")
        tk.Label(title, text="Khaton Studio", fg=TEXT, bg=BG, font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(title, text="A focused editor for the Khaton language  ·  40 commands  ·  17 libraries", fg=MUTED, bg=BG, font=("Segoe UI", 10)).pack(anchor="w")
        toolbar = tk.Frame(header, bg=BG); toolbar.pack(side="right", pady=8)
        for label, command in (("New", self.new_file), ("Open", self.open_file), ("Save", self.save_file), ("Find & Replace", self.find_replace), ("Check", self.check_syntax), ("Run ▶", self.run_code), ("Run Selection", self.run_selection), ("Compile", self.compile_code), ("Save Output", self.save_output)):
            button_style = "Accent.TButton" if label == "Run ▶" else "TButton"
            ttk.Button(toolbar, text=label, command=command, style=button_style).pack(side="left", padx=3)
        ttk.Button(toolbar, text="GitHub ↗", command=lambda: webbrowser.open(GITHUB_URL)).pack(side="left", padx=(10, 0))
        body = tk.PanedWindow(self, orient="vertical", sashrelief="flat", bg=BG, borderwidth=0)
        body.pack(fill="both", expand=True, padx=18, pady=5)
        editor_frame = tk.Frame(body, bg=EDITOR)
        self.editor = tk.Text(editor_frame, bg=EDITOR, fg=TEXT, insertbackground=TEXT, selectbackground="#264f78", undo=True, wrap="none", font=("Consolas", 12), padx=10, pady=8, borderwidth=0)
        self.lines = LineNumbers(editor_frame, self.editor)
        self.lines.pack(side="left", fill="y")
        self.editor.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=self._scroll_editor); scroll.pack(side="right", fill="y")
        self.editor.configure(yscrollcommand=lambda *args: (scroll.set(*args), self.lines.redraw()))
        self.editor.bind("<KeyRelease>", self._on_editor_change); self.editor.bind("<Configure>", self.lines.redraw); self.editor.bind("<MouseWheel>", self.lines.redraw); self.editor.bind("<ButtonRelease-1>", self._update_cursor_status); self.editor.bind("<Control-r>", lambda _: self.run_code()); self.editor.bind("<F5>", lambda _: self.run_code()); self.editor.bind("<Control-f>", lambda _: self.find_replace())
        body.add(editor_frame, minsize=260)
        output_frame = tk.Frame(body, bg=PANEL)
        output_header = tk.Frame(output_frame, bg=PANEL); output_header.pack(fill="x", padx=10, pady=(7, 2))
        tk.Label(output_header, text="Output / diagnostics", bg=PANEL, fg=MUTED, anchor="w").pack(side="left")
        ttk.Button(output_header, text="Clear", command=self.clear_output).pack(side="right")
        self.output = tk.Text(output_frame, height=8, bg="#0b0f14", fg=TEXT, insertbackground=TEXT, font=("Consolas", 10), state="disabled", wrap="word", borderwidth=0, padx=10, pady=8)
        self.output.pack(fill="both", expand=True, padx=8, pady=(0, 8)); body.add(output_frame, minsize=120)
        status_bar = tk.Frame(self, bg="#0b0f14", height=30); status_bar.pack(fill="x", padx=18, pady=(0, 10))
        self.status = tk.Label(status_bar, text="● Ready — Khaton Studio", bg="#0b0f14", fg=GREEN, anchor="w", font=("Segoe UI", 9)); self.status.pack(side="left", padx=10, pady=6)
        tk.Label(status_bar, text="github.com/e3e4e5hoi-star/Khaton", bg="#0b0f14", fg="#758195", anchor="e", font=("Consolas", 8)).pack(side="right", padx=10)
        for tag, color in (("keyword", "#ff7b72"), ("number", "#79c0ff"), ("string", "#a5d6ff"), ("comment", "#8b949e")):
            self.editor.tag_configure(tag, foreground=color)

    def _on_editor_change(self, *_):
        self._highlight(); self._update_cursor_status()
    def _update_cursor_status(self, *_):
        line, column = self.editor.index("insert").split('.')
        self.status.config(text=f"● Ready — line {line}, column {int(column) + 1}", fg=GREEN)
    def _scroll_editor(self, *args):
        self.editor.yview(*args); self.lines.redraw()
    def _load_example(self):
        example = ROOT / "examples" / "hello.kh"
        if example.exists(): self.editor.insert("1.0", example.read_text(encoding="utf-8")); self._highlight()
    def new_file(self): self.editor.delete("1.0", "end"); self.current_file = None; self.status.config(text="New Khaton file")
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Khaton files", "*.kh"), ("All files", "*.*")])
        if path:
            self.editor.delete("1.0", "end"); self.editor.insert("1.0", Path(path).read_text(encoding="utf-8")); self.current_file = Path(path); self._highlight(); self.status.config(text=f"Opened {self.current_file.name}")
    def save_file(self):
        selected = filedialog.asksaveasfilename(defaultextension=".kh", filetypes=[("Khaton files", "*.kh")]) if self.current_file is None else str(self.current_file)
        path = Path(selected) if selected else None
        if path is not None:
            self.current_file = Path(path); self.current_file.write_text(self.editor.get("1.0", "end-1c"), encoding="utf-8"); self.status.config(text=f"Saved {self.current_file.name}")
    def find_replace(self):
        dialog = tk.Toplevel(self)
        dialog.title("Find & Replace")
        dialog.configure(bg=PANEL)
        dialog.resizable(False, False)
        dialog.transient(self)
        fields = tk.Frame(dialog, bg=PANEL); fields.pack(fill="x", padx=14, pady=14)
        tk.Label(fields, text="Find", bg=PANEL, fg=TEXT).grid(row=0, column=0, sticky="w", pady=4)
        find_entry = ttk.Entry(fields, width=36); find_entry.grid(row=0, column=1, padx=(10, 0), pady=4)
        tk.Label(fields, text="Replace with", bg=PANEL, fg=TEXT).grid(row=1, column=0, sticky="w", pady=4)
        replace_entry = ttk.Entry(fields, width=36); replace_entry.grid(row=1, column=1, padx=(10, 0), pady=4)
        buttons = tk.Frame(dialog, bg=PANEL); buttons.pack(fill="x", padx=14, pady=(0, 14))
        def find_next():
            needle = find_entry.get()
            if not needle: return
            start = self.editor.search(needle, self.editor.index("insert"), stopindex="end") or self.editor.search(needle, "1.0", stopindex="end")
            if start:
                end = f"{start}+{len(needle)}c"
                self.editor.tag_remove("sel", "1.0", "end"); self.editor.tag_add("sel", start, end); self.editor.mark_set("insert", end); self.editor.see(start); self._update_cursor_status()
            else: self.status.config(text=f"Not found: {needle}", fg=ERROR)
        def replace_one():
            try:
                start, end = self.editor.index("sel.first"), self.editor.index("sel.last")
                if self.editor.get(start, end) == find_entry.get(): self.editor.delete(start, end); self.editor.insert(start, replace_entry.get()); self._highlight()
            except tk.TclError:
                pass
            find_next()
        def replace_all():
            needle, replacement = find_entry.get(), replace_entry.get()
            if not needle: return
            content = self.editor.get("1.0", "end-1c"); count = content.count(needle)
            if count: self.editor.delete("1.0", "end"); self.editor.insert("1.0", content.replace(needle, replacement)); self._highlight()
            self._write_output(f"Replaced {count} occurrence(s)")
        ttk.Button(buttons, text="Find Next", command=find_next).pack(side="left", padx=3)
        ttk.Button(buttons, text="Replace", command=replace_one).pack(side="left", padx=3)
        ttk.Button(buttons, text="Replace All", command=replace_all).pack(side="left", padx=3)
        ttk.Button(buttons, text="Close", command=dialog.destroy).pack(side="right", padx=3)
        find_entry.focus_set()
    def _write_output(self, text, error=False):
        self.output.configure(state="normal"); self.output.delete("1.0", "end"); self.output.insert("1.0", text); self.output.configure(state="disabled"); self.status.config(text="● Error" if error else "● Finished", fg=ERROR if error else GREEN)
    def clear_output(self):
        self.output.configure(state="normal"); self.output.delete("1.0", "end"); self.output.configure(state="disabled"); self.status.config(text="● Output cleared", fg=MUTED)
    def save_output(self):
        content = self.output.get("1.0", "end-1c")
        if not content.strip():
            self.status.config(text="● No output to save", fg=MUTED)
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], title="Save Khaton output")
        if path:
            Path(path).write_text(content, encoding="utf-8")
            self.status.config(text=f"● Output saved to {Path(path).name}", fg=GREEN)
    def check_syntax(self):
        try:
            parse(self.editor.get("1.0", "end-1c")); self._write_output("Syntax OK")
        except Exception as exc: self._write_output(str(exc), True)
    def run_selection(self):
        try:
            source = self.editor.get("sel.first", "sel.last")
        except tk.TclError:
            self._write_output("Select Khaton code first", True); return
        try:
            result = KhatonRuntime().run(parse(source)); self._write_output("\\n".join(result.output) or "(no output)")
        except Exception as exc: self._write_output(str(exc), True)
    def run_code(self):
        source = self.editor.get("1.0", "end-1c")
        def worker():
            try:
                result = KhatonRuntime().run(parse(source)); output = "\n".join(result.output) or "(no output)"
                self.after(0, lambda: self._write_output(output))
            except Exception as exc: self.after(0, lambda: self._write_output(str(exc), True))
        self.status.config(text="Running…", fg=ACCENT); threading.Thread(target=worker, daemon=True).start()
    def compile_code(self):
        try:
            source = self.editor.get("1.0", "end-1c"); program = compile_source(source)
            path = filedialog.asksaveasfilename(defaultextension=".kbc", filetypes=[("Khaton bytecode", "*.kbc")])
            if path: save_bytecode(program, path); self._write_output(f"Compiled successfully:\n{path}")
        except Exception as exc: self._write_output(str(exc), True)
    def _highlight(self, *_):
        for tag in ("keyword", "number", "string", "comment"): self.editor.tag_remove(tag, "1.0", "end")
        for line_no, line in enumerate(self.editor.get("1.0", "end-1c").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                start = f"{line_no}.0"; self.editor.tag_add("comment", start, f"{line_no}.end"); continue
            first = line.find(stripped.split()[0]) if stripped.split() else -1
            if first >= 0 and stripped.split()[0] in KEYWORDS: self.editor.tag_add("keyword", f"{line_no}.{first}", f"{line_no}.{first + len(stripped.split()[0])}")
            for token in line.split():
                pos = line.find(token)
                if token.isdigit(): self.editor.tag_add("number", f"{line_no}.{pos}", f"{line_no}.{pos+len(token)}")
                elif len(token) >= 2 and token[0] == token[-1] and token[0] in {'\"', "'"}: self.editor.tag_add("string", f"{line_no}.{pos}", f"{line_no}.{pos+len(token)}")
        self.lines.redraw()

def main(): KhatonStudio().mainloop()
if __name__ == "__main__": main()
