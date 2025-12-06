import tkinter as tk
from tkinter import ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Template App")
        self.geometry("400x300")

        self.label = ttk.Label(self, text="Hello, Tkinter!", font=("Helvetica", 16))
        self.label.pack(expand=True)

        self.button = ttk.Button(self, text="Click Me", command=self.on_click)
        self.button.pack(pady=20)

    def on_click(self):
        self.label.config(text="Button Clicked!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
