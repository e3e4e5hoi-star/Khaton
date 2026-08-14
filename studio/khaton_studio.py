from __future__ import annotations
import os
import sys
import threading
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
        self.title("Khaton Studio")
        self.geometry("1100x720")
        self.minsize(800, 520)
        self.configure(bg=BG)
        self.current_file: Path | None = None
        self._build_ui()
        self._load_example()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", background=PANEL, foreground=TEXT, padding=(12, 7), borderwidth=0)
        style.map("TButton", background=[("active", "#263244")])
        header = tk.Frame(self, bg=BG, height=72); header.pack(fill="x", padx=18, pady=(12, 5))
        logo_path = ROOT / "studio" / "assets" / "khaton-camel.jpg"
        if Image and logo_path.exists():
            image = Image.open(logo_path).resize((54, 54))
            self.logo = ImageTk.PhotoImage(image)
            tk.Label(header, image=self.logo, bg=BG).pack(side="left", padx=(0, 12))
        title = tk.Frame(header, bg=BG); title.pack(side="left")
        tk.Label(title, text="Khaton Studio", fg=TEXT, bg=BG, font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(title, text="A colorful editor for the Khaton language", fg=MUTED, bg=BG, font=("Segoe UI", 10)).pack(anchor="w")
        toolbar = tk.Frame(header, bg=BG); toolbar.pack(side="right", pady=8)
        for label, command in (("New", self.new_file), ("Open", self.open_file), ("Save", self.save_file), ("Check", self.check_syntax), ("Run ▶", self.run_code), ("Run Selection", self.run_selection), ("Compile", self.compile_code)):
            ttk.Button(toolbar, text=label, command=command).pack(side="left", padx=3)
        body = tk.PanedWindow(self, orient="vertical", sashrelief="flat", bg=BG, borderwidth=0)
        body.pack(fill="both", expand=True, padx=18, pady=5)
        editor_frame = tk.Frame(body, bg=EDITOR)
        self.editor = tk.Text(editor_frame, bg=EDITOR, fg=TEXT, insertbackground=TEXT, selectbackground="#264f78", undo=True, wrap="none", font=("Consolas", 12), padx=10, pady=8, borderwidth=0)
        self.lines = LineNumbers(editor_frame, self.editor)
        self.lines.pack(side="left", fill="y")
        self.editor.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=self._scroll_editor); scroll.pack(side="right", fill="y")
        self.editor.configure(yscrollcommand=lambda *args: (scroll.set(*args), self.lines.redraw()))
        self.editor.bind("<KeyRelease>", self._on_editor_change); self.editor.bind("<Configure>", self.lines.redraw); self.editor.bind("<MouseWheel>", self.lines.redraw); self.editor.bind("<ButtonRelease-1>", self._update_cursor_status); self.editor.bind("<Control-r>", lambda _: self.run_code()); self.editor.bind("<F5>", lambda _: self.run_code())
        body.add(editor_frame, minsize=260)
        output_frame = tk.Frame(body, bg=PANEL)
        tk.Label(output_frame, text="Output / diagnostics", bg=PANEL, fg=MUTED, anchor="w").pack(fill="x", padx=10, pady=(7, 2))
        self.output = tk.Text(output_frame, height=8, bg="#0b0f14", fg=TEXT, insertbackground=TEXT, font=("Consolas", 10), state="disabled", wrap="word", borderwidth=0, padx=10, pady=8)
        self.output.pack(fill="both", expand=True, padx=8, pady=(0, 8)); body.add(output_frame, minsize=120)
        self.status = tk.Label(self, text="Ready — Khaton Studio", bg=BG, fg=MUTED, anchor="w"); self.status.pack(fill="x", padx=18, pady=(0, 8))
        for tag, color in (("keyword", "#ff7b72"), ("number", "#79c0ff"), ("string", "#a5d6ff"), ("comment", "#8b949e")):
            self.editor.tag_configure(tag, foreground=color)

    def _on_editor_change(self, *_):
        self._highlight(); self._update_cursor_status()
    def _update_cursor_status(self, *_):
        line, column = self.editor.index("insert").split('.')
        self.status.config(text=f"Ready — line {line}, column {int(column) + 1}")
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
    def _write_output(self, text, error=False):
        self.output.configure(state="normal"); self.output.delete("1.0", "end"); self.output.insert("1.0", text); self.output.configure(state="disabled"); self.status.config(text="Error" if error else "Finished", fg=ERROR if error else GREEN)
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
