import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import os

class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Avatar OS")
        self.geometry("1100x700")
        self.resizable(False, False)
        
        # Paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # App Definitions
        self.apps = [
            {"name": "Calculator", "icon": "🧮", "path": "calculator/main.py", "color": "#FF6B6B"},
            {"name": "To-Do List", "icon": "✅", "path": "todo_list/main.py", "color": "#4ECDC4"},
            {"name": "Clock", "icon": "⏰", "path": "digital_clock/main.py", "color": "#45B7D1"},
            {"name": "Text Editor", "icon": "📝", "path": "text_editor/main.py", "color": "#96CEB4"},
            {"name": "Converter", "icon": "📏", "path": "unit_converter/main.py", "color": "#FFEEAD"},
            {"name": "Media Pro", "icon": "🎬", "path": "media_viewer/main.py", "color": "#D4A5A5"},
            {"name": "Browser", "icon": "🌐", "path": "browser/main.py", "color": "#9B59B6"},
            {"name": "Snake", "icon": "🐍", "path": "snake_game/main.py", "color": "#2ECC71"},
            {"name": "Weather", "icon": "🌤️", "path": "weather/main.py", "color": "#F1C40F"},
            {"name": "Music", "icon": "🎵", "path": "music_player/main.py", "color": "#E91E63"},
        ]
        
        self.load_assets()
        self.create_widgets()

    def load_assets(self):
        try:
            bg_path = os.path.join(os.path.dirname(__file__), "bg.png")
            pil_img = Image.open(bg_path)
            # Resize to fill window
            pil_img = pil_img.resize((1100, 700), Image.Resampling.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(pil_img)
        except Exception as e:
            print(f"Error loading background: {e}")
            self.bg_img = None

    def create_widgets(self):
        # Background Canvas
        self.canvas = tk.Canvas(self, width=1100, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        if self.bg_img:
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
        else:
            self.canvas.configure(bg="#1a1a2e")

        # Header
        self.canvas.create_text(550, 80, text="Avatar Ecosystem", font=("Segoe UI", 40, "bold"), fill="white")
        self.canvas.create_text(550, 130, text="Welcome back, User", font=("Segoe UI", 16), fill="#a0a0a0")

        # Grid Calculation
        start_x = 150
        start_y = 200
        cols = 4
        pad_x = 50
        pad_y = 50
        btn_width = 160
        btn_height = 140
        
        for i, app_data in enumerate(self.apps):
            row = i // cols
            col = i % cols
            
            x = start_x + (col * (btn_width + pad_x))
            y = start_y + (row * (btn_height + pad_y))
            
            self.create_app_button(x, y, btn_width, btn_height, app_data)

    def create_app_button(self, x, y, w, h, data):
        # Draw transparent-ish rectangle helper? Tkinter canvas doesn't support alpha well easily.
        # We will place a Frame on the canvas via create_window for interaction.
        
        # Frame for the "Card"
        card = tk.Frame(self, bg="#202020", highlightbackground=data["color"], highlightthickness=1)
        
        # Inner layout
        icon = tk.Label(card, text=data["icon"], font=("Segoe UI Emoji", 40), bg="#202020", fg="white")
        icon.pack(fill="both", expand=True, pady=(10, 0))
        
        title = tk.Label(card, text=data["name"], font=("Segoe UI", 12, "bold"), bg="#202020", fg="white")
        title.pack(side="bottom", pady=(0, 15))
        
        # Bind click
        for widget in (card, icon, title):
            widget.bind("<Button-1>", lambda e, p=data["path"]: self.launch_app(p))
            widget.bind("<Enter>", lambda e, c=card: c.config(bg="#303030"))
            widget.bind("<Leave>", lambda e, c=card: c.config(bg="#202020"))
            
            if widget != card:
                widget.bind("<Enter>", lambda e, c=card: c.config(bg="#303030"))
                widget.bind("<Leave>", lambda e, c=card: c.config(bg="#202020"))

        self.canvas.create_window(x, y, width=w, height=h, window=card, anchor="nw")

    def launch_app(self, script_path):
        full_path = os.path.join(self.base_dir, script_path)
        if not os.path.exists(full_path):
            messagebox.showerror("Error", f"App not found: {full_path}")
            return
            
        try:
            # Launch independently
            subprocess.Popen([sys.executable, full_path], cwd=self.base_dir)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch: {e}")

def main():
    app = DashboardApp()
    app.mainloop()

if __name__ == "__main__":
    main()
