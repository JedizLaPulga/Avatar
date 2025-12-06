import tkinter as tk
from tkinter import ttk
import time

class DigitalClockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Clock")
        self.geometry("400x200")
        self.configure(bg='black')
        
        self.create_widgets()
        self.update_clock()

    def create_widgets(self):
        self.time_label = tk.Label(self, font=('calibri', 40, 'bold'),
                                   background='black',
                                   foreground='white')
        self.time_label.pack(expand=True)
        
        self.date_label = tk.Label(self, font=('calibri', 20),
                                   background='black',
                                   foreground='gray')
        self.date_label.pack(pady=10)

    def update_clock(self):
        current_time = time.strftime('%H:%M:%S')
        current_date = time.strftime('%A, %B %d, %Y')
        
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        
        self.after(1000, self.update_clock)

if __name__ == "__main__":
    app = DigitalClockApp()
    app.mainloop()
