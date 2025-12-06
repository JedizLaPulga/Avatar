import tkinter as tk
from tkinter import ttk

class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("600x500") # Widened window for history
        
        self.result_var = tk.StringVar()
        self.dark_mode = False
        
        # Define colors and fonts
        self.light_theme = {
            "bg": "#f0f0f0", "fg": "#000000",
            "btn_bg": "#ffffff", "btn_fg": "#000000",
            "display_bg": "#ffffff", "display_fg": "#000000",
            "history_bg": "#e0e0e0", "history_fg": "#000000"
        }
        self.dark_theme = {
            "bg": "#2e2e2e", "fg": "#ffffff",
            "btn_bg": "#444444", "btn_fg": "#ffffff",
            "display_bg": "#1e1e1e", "display_fg": "#ffffff",
            "history_bg": "#222222", "history_fg": "#dddddd"
        }
        self.current_theme = self.light_theme
        self.default_font = ("Arial", 14, "bold")
        self.display_font = ("Arial", 24, "bold")
        self.history_font = ("Arial", 12)

        self.create_widgets()
        self.bind_keys()
        self.apply_theme()

    def create_widgets(self):
        # Top-level layout frame
        self.layout_frame = tk.Frame(self)
        self.layout_frame.pack(fill="both", expand=True)

        # Left Side: Calculator UI
        self.left_frame = tk.Frame(self.layout_frame)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right Side: History UI
        self.right_frame = tk.Frame(self.layout_frame, width=200)
        self.right_frame.pack(side="right", fill="both", padx=5, pady=5)

        # --- Calculator Components (Left Frame) ---
        
        # Header with Theme Toggle
        self.header_frame = tk.Frame(self.left_frame)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        
        self.theme_btn = tk.Button(self.header_frame, text="🌙 Dark Mode", command=self.toggle_theme, bd=0, font=("Arial", 10, "bold"), cursor="hand2")
        self.theme_btn.pack(side="right") # Theme button on calculator side

        # Display
        self.display = tk.Entry(self.left_frame, textvariable=self.result_var, font=self.display_font, justify="right", bd=0, highlightthickness=1)
        self.display.pack(fill="x", padx=10, pady=10, ipady=10)
        
        # Buttons Grid
        self.buttons_frame = tk.Frame(self.left_frame)
        self.buttons_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        buttons = [
            ('C', 0, 0), ('(', 0, 1), (')', 0, 2), ('/', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('*', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2, 2) # spanning 2 columns
        ]
        
        self.btn_widgets = {} 
        
        for item in buttons:
            text = item[0]
            row = item[1]
            col = item[2]
            colspan = item[3] if len(item) > 3 else 1
            
            if text == '=':
                cmd = self.calculate
            elif text == 'C':
                cmd = self.clear_display
            else:
                cmd = lambda t=text: self.append_to_display(t)
                
            btn = tk.Button(self.buttons_frame, text=text, command=cmd, font=self.default_font, bd=0)
            btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=3, pady=3)
            self.btn_widgets[text] = btn

        # Configure Grid Weights
        for i in range(5):
            self.buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
            
        # --- History Components (Right Frame) ---
        
        self.history_label = tk.Label(self.right_frame, text="History", font=("Arial", 12, "bold"))
        self.history_label.pack(side="top", pady=5)
        
        self.clear_history_btn = tk.Button(self.right_frame, text="Clear History", command=self.clear_history, font=("Arial", 10, "bold"), bd=0, cursor="hand2")
        self.clear_history_btn.pack(side="bottom", fill="x", padx=5, pady=5)
        
        # Frame for list and scrollbar
        list_frame = tk.Frame(self.right_frame)
        list_frame.pack(side="top", fill="both", expand=True)
        
        self.history_list = tk.Listbox(list_frame, font=self.history_font, bd=0, highlightthickness=0)
        self.history_list.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_list.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.history_list.config(yscrollcommand=self.scrollbar.set)

    def bind_keys(self):
        self.bind('<Return>', lambda event: self.calculate())
        self.bind('<BackSpace>', lambda event: self.handle_backspace())
        self.bind('<Escape>', lambda event: self.clear_display())
        # Bind numbers and operators
        for key in '0123456789.+-*/()':
            self.bind(key, lambda event, k=key: self.append_to_display(k))

    def handle_backspace(self):
        current_text = self.result_var.get()
        self.result_var.set(current_text[:-1])

    def append_to_display(self, text):
        current_text = self.result_var.get()
        # Prevent multiple decimals in a number (simple check)
        if text == '.' and current_text and current_text[-1] == '.':
            return
        self.result_var.set(current_text + text)
        self.display.icursor(tk.END) # move cursor to end

    def clear_display(self):
        self.result_var.set("")

    def calculate(self):
        try:
            expression = self.result_var.get()
            allowed_chars = set("0123456789.+-*/() ")
            if not all(c in allowed_chars for c in expression):
                 self.result_var.set("Error")
                 return
                 
            result = eval(expression)
            self.result_var.set(str(result))
            
            # Add to history
            self.history_list.insert(0, f"{expression} = {result}")
            
        except Exception:
            self.result_var.set("Error")

    def clear_history(self):
        self.history_list.delete(0, tk.END)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.current_theme = self.dark_theme if self.dark_mode else self.light_theme
        self.theme_btn.config(text="☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        self.apply_theme()

    def apply_theme(self):
        colors = self.current_theme
        
        self.configure(bg=colors["bg"])
        self.layout_frame.configure(bg=colors["bg"])
        self.left_frame.configure(bg=colors["bg"])
        self.right_frame.configure(bg=colors["bg"])
        self.header_frame.configure(bg=colors["bg"])
        self.buttons_frame.configure(bg=colors["bg"])
        
        # Theme Button
        self.theme_btn.configure(bg=colors["bg"], fg=colors["fg"], activebackground=colors["bg"], activeforeground=colors["fg"])

        # Display
        self.display.configure(bg=colors["display_bg"], fg=colors["display_fg"], insertbackground=colors["fg"])
        
        # History
        self.history_label.configure(bg=colors["bg"], fg=colors["fg"])
        self.history_list.configure(bg=colors["history_bg"], fg=colors["history_fg"])
        self.clear_history_btn.configure(bg=colors["btn_bg"], fg=colors["btn_fg"], activebackground=colors["fg"], activeforeground=colors["bg"])
        
        # Buttons
        for text, btn in self.btn_widgets.items():
            if text == '=':
                btn.configure(bg="#ff9500" if self.dark_mode else "#ffaa00", fg="white")
            else:
                btn.configure(bg=colors["btn_bg"], fg=colors["btn_fg"])
            
            btn.configure(activebackground=colors["fg"], activeforeground=colors["bg"])

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
