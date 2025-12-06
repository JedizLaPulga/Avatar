import tkinter as tk
from tkinter import ttk
import time

class DigitalClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Clock & Stopwatch")
        self.geometry("500x300")
        self.configure(bg='black')
        
        # Apply dark theme for ttk widgets
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure("TNotebook", background="#222222", borderwidth=0)
        style.configure("TNotebook.Tab", background="#444444", foreground="white", font=('Arial', 10, 'bold'), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#007acc")], foreground=[("selected", "white")])
        style.configure("TFrame", background="#222222")

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.clock_frame = ttk.Frame(self.notebook)
        self.stopwatch_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.clock_frame, text='Clock')
        self.notebook.add(self.stopwatch_frame, text='Stopwatch')
        
        # --- Clock ---
        self.setup_clock()
        
        # --- Stopwatch ---
        self.stopwatch_running = False
        self.stopwatch_counter = 0 # in hundredths of seconds
        self.setup_stopwatch()

    def setup_clock(self):
        self.time_label = tk.Label(self.clock_frame, font=('calibri', 60, 'bold'),
                                   background='#222222', foreground='white')
        self.time_label.pack(expand=True, pady=(40, 0))
        
        self.date_label = tk.Label(self.clock_frame, font=('calibri', 20),
                                   background='#222222', foreground='gray')
        self.date_label.pack(pady=20)
        
        self.update_clock()

    def update_clock(self):
        current_time = time.strftime('%H:%M:%S')
        current_date = time.strftime('%A, %B %d, %Y')
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        self.after(1000, self.update_clock)

    def setup_stopwatch(self):
        self.sw_label = tk.Label(self.stopwatch_frame, text="00:00:00", font=('calibri', 60, 'bold'),
                                 background='#222222', foreground='white')
        self.sw_label.pack(expand=True, pady=(30, 0))

        btn_frame = ttk.Frame(self.stopwatch_frame)
        btn_frame.pack(pady=30)

        # Start/Stop Button
        self.sw_start_btn = tk.Button(btn_frame, text="Start", command=self.toggle_stopwatch, 
                                      bg='#28a745', fg='white', font=('Arial', 12, 'bold'), width=10, bd=0)
        self.sw_start_btn.pack(side="left", padx=10)

        # Reset Button
        self.sw_reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_stopwatch, 
                                      bg='#dc3545', fg='white', font=('Arial', 12, 'bold'), width=10, bd=0)
        self.sw_reset_btn.pack(side="left", padx=10)
    
    def toggle_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_running = False
            self.sw_start_btn.config(text="Start", bg='#28a745') # Green for start
        else:
            self.stopwatch_running = True
            self.sw_start_btn.config(text="Stop", bg='#ffc107', fg='black') # Yellow/Orange for stop
            self.update_stopwatch()

    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_counter = 0
        self.sw_label.config(text="00:00:00")
        self.sw_start_btn.config(text="Start", bg='#28a745', fg='white')

    def update_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_counter += 1
            
            # Simple milliseconds -> formatted time logic
            total_seconds = self.stopwatch_counter // 100
            milli = self.stopwatch_counter % 100
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            
            time_string = f"{minutes:02}:{seconds:02}:{milli:02}"
            self.sw_label.config(text=time_string)
            
            # Update every 10ms (approx)
            self.after(10, self.update_stopwatch)

if __name__ == "__main__":
    app = DigitalClockApp()
    app.mainloop()
