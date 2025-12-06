import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw

class DrawingBoardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Canvas Pro")
        self.geometry("1000x700")
        
        # State
        self.brush_color = "black"
        self.brush_size = 5
        self.old_x = None
        self.old_y = None
        
        # Image for saving
        self.image = Image.new("RGB", (1000, 600), "white")
        self.draw = ImageDraw.Draw(self.image)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Tools Frame (Left Sidebar)
        tools_frame = tk.Frame(self, bg="#2c3e50", width=100)
        tools_frame.pack(side="left", fill="y")
        
        # Color Palette
        tk.Label(tools_frame, text="Colors", bg="#2c3e50", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        colors = ["black", "red", "green", "blue", "yellow", "orange", "purple", "white"]
        for c in colors:
            btn = tk.Frame(tools_frame, bg=c, width=30, height=30, cursor="hand2")
            btn.pack(pady=5)
            btn.bind("<Button-1>", lambda e, col=c: self.set_color(col))
            
        # Custom Color
        tk.Button(tools_frame, text="🎨 Pick", command=self.pick_color, bg="#34495e", fg="white", bd=0).pack(pady=10, fill="x", padx=5)

        # Brush Size
        tk.Label(tools_frame, text="Size", bg="#2c3e50", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
        self.size_scale = tk.Scale(tools_frame, from_=1, to=20, orient="vertical", bg="#2c3e50", fg="white", highlightthickness=0)
        self.size_scale.set(5)
        self.size_scale.pack()
        self.size_scale.bind("<Motion>", self.change_size)

        # Actions
        tk.Label(tools_frame, text="Actions", bg="#2c3e50", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=10)
        tk.Button(tools_frame, text="🗑️ Clear", command=self.clear_canvas, bg="#c0392b", fg="white", bd=0).pack(pady=5, fill="x", padx=5)
        tk.Button(tools_frame, text="💾 Save", command=self.save_canvas, bg="#27ae60", fg="white", bd=0).pack(pady=5, fill="x", padx=5)

        # Canvas Area
        self.canvas = tk.Canvas(self, bg="white", width=900, height=700)
        self.canvas.pack(side="right", fill="both", expand=True)
        
        # Binds
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        
    def set_color(self, color):
        self.brush_color = color
        
    def pick_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.brush_color = color
            
    def change_size(self, event):
        self.brush_size = self.size_scale.get()
        
    def paint(self, event):
        if self.old_x and self.old_y:
            # Draw on Tkinter Canvas
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y, 
                                    width=self.brush_size, fill=self.brush_color, 
                                    capstyle="round", smooth=True)
            
            # Draw on PIL Image (for saving)
            # Basic line drawing - note: capstyle simulation in PIL is limited in draw.line
            self.draw.line([self.old_x, self.old_y, event.x, event.y], 
                           fill=self.brush_color, width=self.brush_size)
            
        self.old_x = event.x
        self.old_y = event.y
        
    def reset(self, event):
        self.old_x = None
        self.old_y = None
        
    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (1000, 700), "white")
        self.draw = ImageDraw.Draw(self.image)
        
    def save_canvas(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            try:
                self.image.save(file_path)
                messagebox.showinfo("Saved", "Artwork saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    app = DrawingBoardApp()
    app.mainloop()
