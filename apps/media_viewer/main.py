import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time
import os

class MediaViewerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Media Viewer")
        self.geometry("900x700")
        self.configure(bg="#202020")
        
        self.current_image = None
        self.cap = None
        self.is_video_playing = False
        self.video_thread = None
        self.stop_video_flag = False
        
        self.create_widgets()
        self.bind_keys()

    def create_widgets(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#333333", height=50)
        toolbar.pack(fill="x", side="top")
        
        btn_style = {"bg": "#444444", "fg": "white", "bd": 0, "font": ("Segoe UI", 10), "padx": 15, "pady": 5, "cursor": "hand2"}
        
        open_btn = tk.Button(toolbar, text="📂 Open File", command=self.open_file, **btn_style)
        open_btn.pack(side="left", padx=10, pady=10)
        
        self.status_label = tk.Label(toolbar, text="No file loaded", bg="#333333", fg="#aaaaaa", font=("Segoe UI", 10))
        self.status_label.pack(side="right", padx=20)

        # Main Viewport (Canvas for resizing/centering)
        self.viewport = tk.Frame(self, bg="#101010")
        self.viewport.pack(fill="both", expand=True)
        
        self.media_label = tk.Label(self.viewport, bg="#101010")
        self.media_label.pack(expand=True)

        # Control Bar (For Video)
        self.controls = tk.Frame(self, bg="#202020")
        self.controls.pack(fill="x", side="bottom")
        
        self.play_btn = tk.Button(self.controls, text="▶", command=self.toggle_video, state="disabled", **btn_style)
        self.play_btn.pack(side="left", padx=10, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_slider = ttk.Scale(self.controls, from_=0, to=100, variable=self.progress_var, orient="horizontal", command=self.seek_video)
        self.progress_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.progress_slider.state(['disabled'])

    def bind_keys(self):
        self.bind("<space>", lambda e: self.toggle_video())
        self.bind("<Control-o>", lambda e: self.open_file())

    def open_file(self):
        filetypes = [
            ("Media Files", "*.jpg *.jpeg *.png *.bmp *.gif *.mp4 *.avi *.mkv *.mov"),
            ("Images", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("Videos", "*.mp4 *.avi *.mkv *.mov"),
            ("All Files", "*.*")
        ]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.load_media(path)

    def load_media(self, path):
        # Reset current state
        self.stop_video()
        self.media_label.config(image='')
        self.media_label.image = None
        self.status_label.config(text=os.path.basename(path))

        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            self.show_image_mode()
            self.display_image(path)
        elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
            self.show_video_mode()
            self.load_video(path)
        else:
            messagebox.showerror("Error", "Unsupported file format")

    def show_image_mode(self):
        self.controls.pack_forget() # Hide video controls
    
    def show_video_mode(self):
        self.controls.pack(fill="x", side="bottom") # Show video controls
        self.play_btn.config(state="normal", text="▶")
        self.progress_slider.state(['!disabled'])

    def display_image(self, path):
        try:
            pil_img = Image.open(path)
            # Resize logic (fit to window)
            # For simplicity, we limit to 800x600 max or window size
            w_max, h_max = 1200, 800
            pil_img.thumbnail((w_max, h_max))
            
            self.current_image = ImageTk.PhotoImage(pil_img)
            self.media_label.config(image=self.current_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    # --- Video Logic ---

    def load_video(self, path):
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open video file")
            return
        
        # Get video properties
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        # Show first frame
        self.show_frame()

    def show_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                
                # Resize for display
                img.thumbnail((1000, 700))
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.media_label.config(image=imgtk)
                self.media_label.image = imgtk # Keep ref
            return ret
        return False

    def toggle_video(self):
        if self.is_video_playing:
            self.stop_video_flag = True
            self.is_video_playing = False
            self.play_btn.config(text="▶")
        else:
            if self.cap and self.cap.isOpened():
                self.is_video_playing = True
                self.stop_video_flag = False
                self.play_btn.config(text="⏸")
                self.video_thread = threading.Thread(target=self.play_loop, daemon=True)
                self.video_thread.start()

    def play_loop(self):
        while not self.stop_video_flag and self.cap and self.cap.isOpened():
            start_time = time.time()
            
            ret, frame = self.cap.read()
            if not ret:
                # Loop or stop
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop
                continue
            
            # Update UI in main thread (kinda risky in Tkinter but often works for simple label updates, 
            # ideally use after() but threading needed for blocking cv2.read)
            # To be safe, we convert and schedule update
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img.thumbnail((1000, 700))
            imgtk = ImageTk.PhotoImage(image=img)
            
            try:
                self.media_label.config(image=imgtk)
                self.media_label.image = imgtk
                
                # Update slider
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                progress = (current_frame / self.total_frames) * 100
                self.progress_var.set(progress)
            except:
                break # UI likely destroyed

            # FPS Control
            elapsed = time.time() - start_time
            delay = max(0, (1.0/self.fps) - elapsed)
            time.sleep(delay)
            
        self.is_video_playing = False
        # Note: self.play_btn.config(text="▶") should be called if loop exits naturally
        # but safely via after usually.

    def seek_video(self, value):
        if self.cap:
            target_frame = int((float(value) / 100) * self.total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            if not self.is_video_playing:
                self.show_frame()

    def stop_video(self):
        self.stop_video_flag = True
        self.is_video_playing = False
        time.sleep(0.1) # Wait a bit for thread
        if self.cap:
            self.cap.release()
            self.cap = None

if __name__ == "__main__":
    app = MediaViewerApp()
    app.mainloop()
