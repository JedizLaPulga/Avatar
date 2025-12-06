import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
import os

class EditorTab(tk.Frame):
    def __init__(self, parent, app_theme):
        super().__init__(parent)
        self.file_path = None
        self.is_modified = False
        self.app_theme = app_theme
        
        # Grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Text Area with Scrollbar
        self.text_area = tk.Text(self, undo=True, wrap="word", relief="flat", padx=10, pady=10)
        self.text_area.grid(row=0, column=0, sticky="nsew")
        
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_area.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_area['yscrollcommand'] = self.scrollbar.set

        # Bind events
        self.text_area.bind("<<Modified>>", self._on_modified)
        self.text_area.bind("<Control-MouseWheel>", self._on_zoom)

        # Initial Font
        self.current_font_size = 12
        self.update_font()
        self.apply_theme(app_theme)

    def _on_modified(self, event=None):
        if self.text_area.edit_modified():
            self.is_modified = True
            # We reset the modify flag so we can detect future changes, 
            # but we keep our own internal is_modified True until saved.
            # However, for a simple notepad, just knowing *something* changed is often enough.
            # A more complex impl would track undo stack depth.
            self.text_area.edit_modified(False) 

    def _on_zoom(self, event):
        if event.delta > 0:
            self.current_font_size += 1
        else:
            self.current_font_size = max(6, self.current_font_size - 1)
        self.update_font()
        return "break" # prevent scrolling

    def update_font(self):
        font = tkfont.Font(family="Consolas", size=self.current_font_size)
        self.text_area.configure(font=font)

    def apply_theme(self, theme):
        self.app_theme = theme
        self.text_area.config(
            bg=theme["bg"], 
            fg=theme["fg"], 
            insertbackground=theme["fg"], # cursor color
            selectbackground=theme["select_bg"],
            selectforeground=theme["select_fg"]
        )

class TextEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notepad Enhanced")
        self.geometry("800x600")
        
        # Themes
        self.light_theme = {
            "bg": "#ffffff", "fg": "#000000", 
            "select_bg": "#0078d7", "select_fg": "#ffffff",
            "frame_bg": "#f3f3f3"
        }
        self.dark_theme = {
            "bg": "#1e1e1e", "fg": "#d4d4d4", 
            "select_bg": "#264f78", "select_fg": "#ffffff",
            "frame_bg": "#121212"
        }
        self.dark_mode = False
        self.current_theme = self.light_theme

        self.create_widgets()
        self.create_menu()
        self.bind_keys()
        
        # Add initial tab
        self.add_new_tab()

    def create_widgets(self):
        # Toolbar Frame
        self.toolbar_frame = tk.Frame(self, bg=self.current_theme["frame_bg"], height=30)
        self.toolbar_frame.pack(fill="x", side="top")
        
        # Theme Toggle Button
        self.theme_btn = tk.Button(self.toolbar_frame, text="🌙 Theme", command=self.toggle_theme, 
                                   bd=0, relief="flat", font=("Segoe UI", 9))
        self.theme_btn.pack(side="right", padx=10, pady=2)

        # Notebook (Tabs) Frame
        self.notebook_frame = tk.Frame(self, bg=self.current_theme["frame_bg"])
        self.notebook_frame.pack(fill="both", expand=True)
        
        # Custom style for notebook to look more modern
        self.style = ttk.Style(self)
        self.style.theme_use('default')
        
        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        # Status Bar
        self.status_bar = tk.Label(self.notebook_frame, text="Ln 1, Col 1", anchor='e', padx=10,
                                   bg=self.current_theme["frame_bg"], fg=self.current_theme["fg"])
        self.status_bar.pack(side="bottom", fill="x")
        
        # Periodically update status
        self.update_status()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Tab", accelerator="Ctrl+N", command=self.add_new_tab)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_current_tab)
        file_menu.add_command(label="Exit", command=self.quit)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self.get_current_text_widget().edit_undo())
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self.get_current_text_widget().edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.focus_get().event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.focus_get().event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.focus_get().event_generate("<<Paste>>"))

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", accelerator="F12", command=self.toggle_theme)

    def bind_keys(self):
        self.bind("<Control-n>", lambda e: self.add_new_tab())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_as_file())
        self.bind("<Control-w>", lambda e: self.close_current_tab())
        self.bind("<F12>", lambda e: self.toggle_theme())

    def get_current_tab(self):
        try:
            tab_id = self.notebook.select()
            if not tab_id:
                return None
            return self.notebook.nametowidget(tab_id)
        except:
            return None

    def get_current_text_widget(self):
        tab = self.get_current_tab()
        if tab:
            return tab.text_area
        return None

    def add_new_tab(self, name="Untitled"):
        tab = EditorTab(self.notebook, self.current_theme)
        self.notebook.add(tab, text=name)
        self.notebook.select(tab)
        
    def close_current_tab(self):
        tab = self.get_current_tab()
        if not tab: return
        # Simple check for simple app: warn if potentially lost? 
        # For this demo, we just close.
        self.notebook.forget(tab)
        if self.notebook.index("end") == 0:
             self.add_new_tab() # Ensure one tab exists

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()
            self.add_new_tab(name=os.path.basename(file_path))
            tab = self.get_current_tab()
            tab.text_area.insert("1.0", content)
            tab.file_path = file_path
            tab.is_modified = False

    def save_file(self):
        tab = self.get_current_tab()
        if not tab: return
        if tab.file_path:
            self._write_to_file(tab.file_path, tab)
        else:
            self.save_as_file()

    def save_as_file(self):
        tab = self.get_current_tab()
        if not tab: return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self._write_to_file(file_path, tab)
            self.notebook.tab(tab, text=os.path.basename(file_path))
            tab.file_path = file_path

    def _write_to_file(self, path, tab):
        try:
            content = tab.text_area.get("1.0", "end-1c")
            with open(path, "w") as f:
                f.write(content)
            tab.is_modified = False
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def update_status(self):
        text_widget = self.get_current_text_widget()
        if text_widget:
            # Get cursor position
            # 'insert' is the insertion cursor
            index = text_widget.index("insert")
            line, col = index.split('.')
            self.status_bar.config(text=f"Ln {line}, Col {int(col)+1} | {'Changed' if self.get_current_tab().is_modified else 'Saved'}")
        
        self.after(100, self.update_status)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.current_theme = self.dark_theme if self.dark_mode else self.light_theme
        self.apply_theme()

    def apply_theme(self):
        theme = self.current_theme
        
        # Configure Main Window
        self.configure(bg=theme["frame_bg"]) # Window bg
        self.notebook_frame.configure(bg=theme["frame_bg"])
        self.toolbar_frame.configure(bg=theme["frame_bg"])
        self.status_bar.configure(bg=theme["frame_bg"], fg=theme["fg"])
        
        # Configure Toolbar Button
        self.theme_btn.configure(bg=theme["select_bg"], fg=theme["select_fg"], 
                                 activebackground=theme["fg"], activeforeground=theme["bg"])
        self.theme_btn.configure(text="☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        
        # Configure Notebook tabs style
        self.style.configure("TNotebook", background=theme["frame_bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=theme["frame_bg"], foreground=theme["fg"])
        self.style.map("TNotebook.Tab", 
                       background=[("selected", theme["bg"])], 
                       foreground=[("selected", theme["fg"])])
        
        # Apply to all tabs
        for tab_id in self.notebook.tabs():
            tab = self.notebook.nametowidget(tab_id)
            tab.apply_theme(theme)

if __name__ == "__main__":
    app = TextEditorApp()
    app.mainloop()
