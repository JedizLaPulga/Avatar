import tkinter as tk
from tkinter import ttk, messagebox

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("400x450")
        
        self.tasks = []
        
        self.create_widgets()

    def create_widgets(self):
        # Input frame
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)
        
        self.task_entry = ttk.Entry(input_frame, width=30)
        self.task_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        add_btn.pack(side=tk.LEFT)
        
        # Listbox
        self.tasks_listbox = tk.Listbox(self, width=50, height=15)
        self.tasks_listbox.pack(pady=10, padx=10)
        
        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        del_btn = ttk.Button(btn_frame, text="Delete Task", command=self.delete_task)
        del_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_all_tasks)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def add_task(self):
        task = self.task_entry.get()
        if task != "":
            self.tasks.append(task)
            self.update_listbox()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "You must enter a task.")

    def delete_task(self):
        try:
            task_index = self.tasks_listbox.curselection()[0]
            del self.tasks[task_index]
            self.update_listbox()
        except:
            messagebox.showwarning("Warning", "You must select a task to delete.")

    def clear_all_tasks(self):
        self.tasks = []
        self.update_listbox()

    def update_listbox(self):
        self.tasks_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.tasks_listbox.insert(tk.END, task)

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
