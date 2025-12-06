import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from datetime import datetime

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("400x600")
        
        # Color Palette (Modern Dark)
        self.colors = {
            "bg": "#121212",
            "card_bg": "#1e1e1e",
            "text": "#e0e0e0",
            "text_dim": "#757575",
            "accent": "#bb86fc",
            "accent_hover": "#9965f4",
            "danger": "#cf6679",
            "success": "#03dac6"
        }
        
        self.configure(bg=self.colors["bg"])
        
        # Fonts
        self.title_font = tkfont.Font(family="Arial", size=24, weight="bold")
        self.task_font = tkfont.Font(family="Arial", size=12)
        self.task_strike_font = tkfont.Font(family="Arial", size=12, overstrike=1)
        
        self.tasks = [] # List of dicts: {'text': str, 'completed': bool, 'id': int}
        self.task_counter = 0

        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg=self.colors["bg"])
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = tk.Label(header_frame, text="My Tasks", font=self.title_font, 
                         bg=self.colors["bg"], fg=self.colors["text"])
        title.pack(side="left")
        
        count_label = tk.Label(header_frame, text=f"{len(self.tasks)} Tasks", 
                               font=("Arial", 10), bg=self.colors["bg"], fg=self.colors["text_dim"])
        count_label.pack(side="right", anchor="s", pady=5)
        self.count_label = count_label

        # Input Area
        input_frame = tk.Frame(self, bg=self.colors["bg"])
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Styled Entry
        self.task_entry = tk.Entry(input_frame, font=("Arial", 12), 
                                   bg=self.colors["card_bg"], fg=self.colors["text"],
                                   insertbackground=self.colors["text"], relief="flat")
        self.task_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        
        # Add Button
        add_btn = tk.Button(input_frame, text="+", font=("Arial", 16, "bold"),
                            bg=self.colors["accent"], fg="#000000",
                            activebackground=self.colors["accent_hover"], activeforeground="#000000",
                            relief="flat", cursor="hand2", command=self.add_task,
                            width=3)
        add_btn.pack(side="right")
        self.bind('<Return>', lambda e: self.add_task())

        # Scrollable Task List Area
        self.canvas = tk.Canvas(self, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg"])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=380) # Adjust width dynamically later?
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)
        self.scrollbar.pack(side="right", fill="y")
        
        # Handle resize for canvas window width
        self.canvas.bind('<Configure>', self.on_canvas_configure)

    def on_canvas_configure(self, event):
        # Update the width of the frame to match the canvas
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def add_task(self):
        text = self.task_entry.get().strip()
        if text:
            self.task_counter += 1
            timestamp = datetime.now().strftime("%I:%M %p")
            task = {'id': self.task_counter, 'text': text, 'completed': False, 'time': timestamp}
            self.tasks.append(task)
            self.task_entry.delete(0, 'end')
            self.render_tasks()

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.render_tasks()

    def toggle_task(self, task_id):
        for t in self.tasks:
            if t['id'] == task_id:
                t['completed'] = not t['completed']
                break
        self.render_tasks()

    def render_tasks(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.count_label.config(text=f"{len(self.tasks)} Tasks")

        for task in self.tasks:
            self.create_task_widget(task)

    def create_task_widget(self, task):
        # Card Frame
        card = tk.Frame(self.scrollable_frame, bg=self.colors["card_bg"], pady=10, padx=10)
        card.pack(fill="x", pady=5)
        
        # Click on card to toggle
        card.bind("<Button-1>", lambda e, tid=task['id']: self.toggle_task(tid))

        # Check Circle (simulated with Label)
        check_char = "✓" if task['completed'] else " "
        check_fg = self.colors["success"] if task['completed'] else self.colors["text_dim"]
        check_bg = self.colors["bg"] # Darker dot
        
        check_lbl = tk.Label(card, text=check_char, font=("Arial", 12, "bold"),
                             bg=check_bg, fg=check_fg, width=3, height=1, cursor="hand2")
        check_lbl.pack(side="left", padx=(0, 10))
        check_lbl.bind("<Button-1>", lambda e, tid=task['id']: self.toggle_task(tid))

        # Text Content (Title + Timestamp)
        content_frame = tk.Frame(card, bg=self.colors["card_bg"])
        content_frame.pack(side="left", fill="x", expand=True)
        content_frame.bind("<Button-1>", lambda e, tid=task['id']: self.toggle_task(tid))

        text_font = self.task_strike_font if task['completed'] else self.task_font
        text_fg = self.colors["text_dim"] if task['completed'] else self.colors["text"]
        
        lbl = tk.Label(content_frame, text=task['text'], font=text_font, bg=self.colors["card_bg"], fg=text_fg, anchor="w")
        lbl.pack(fill="x", expand=True)
        lbl.bind("<Button-1>", lambda e, tid=task['id']: self.toggle_task(tid))
        
        time_lbl = tk.Label(content_frame, text=task.get('time', ''), font=("Arial", 9), 
                            bg=self.colors["card_bg"], fg=self.colors["text_dim"], anchor="w")
        time_lbl.pack(fill="x", expand=True)
        time_lbl.bind("<Button-1>", lambda e, tid=task['id']: self.toggle_task(tid))

        # Delete Button
        del_btn = tk.Label(card, text="✕", font=("Arial", 10, "bold"),
                           bg=self.colors["card_bg"], fg=self.colors["danger"], 
                           cursor="hand2")
        del_btn.pack(side="right", padx=5)
        del_btn.bind("<Button-1>", lambda e, tid=task['id']: self.delete_task(tid))

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
