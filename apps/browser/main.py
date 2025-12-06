import tkinter as tk
from tkinter import messagebox
from tkinterweb import HtmlFrame # pip install tkinterweb
import sys

class BrowserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyBrowser - TkinterWeb")
        self.geometry("1000x800")
        
        self.create_widgets()

    def create_widgets(self):
        # Toolbar
        self.toolbar = tk.Frame(self, bg="#f0f0f0", height=40)
        self.toolbar.pack(fill="x", side="top")
        
        # Navigation Buttons
        btn_style = {"bg": "#e0e0e0", "bd": 1, "relief": "raised", "font": ("Segoe UI", 9)}
        
        tk.Button(self.toolbar, text="<", width=3, command=self.go_back, **btn_style).pack(side="left", padx=2, pady=5)
        self.reload_btn = tk.Button(self.toolbar, text="R", width=3, command=self.reload_page, **btn_style)
        self.reload_btn.pack(side="left", padx=2, pady=5)
        
        # Address Bar
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(self.toolbar, textvariable=self.url_var, font=("Segoe UI", 10))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.url_entry.bind("<Return>", self.load_url)
        
        tk.Button(self.toolbar, text="Go", width=4, command=self.load_url, **btn_style).pack(side="left", padx=2, pady=5)

        # Browser Frame
        self.browser_frame = HtmlFrame(self, horizontal_scrollbar="auto")
        self.browser_frame.pack(fill="both", expand=True)

        # Initial Load
        self.url_var.set("https://www.google.com")
        self.load_url()

    def load_url(self, event=None):
        url = self.url_var.get()
        if not url.startswith("http"):
            url = "https://" + url
            self.url_var.set(url)
        
        try:
            self.browser_frame.load_website(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page: {e}")

    def go_back(self):
        # tkinterweb doesn't expose a simple history stack publicly in strict API 
        # normally, but let's just reload for now or simulate if possible.
        # Actually, standard widget usage focuses on loading content.
        messagebox.showinfo("Info", "Back navigation not supported in this lightweight engine.")

    def reload_page(self):
        self.load_url()

if __name__ == "__main__":
    app = BrowserApp()
    app.mainloop()
