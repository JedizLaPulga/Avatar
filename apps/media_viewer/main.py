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
        self.title("Media Viewer Pro")
        self.geometry("1000x700")
        self.configure(bg="#121212")
        
        self.current_image = None
        self.pil_image = None # Original loaded image for transforms
        
        self.cap = None
        self.is_video_playing = False
        self.video_thread = None
        self.stop_video_flag = False
        
        self.zoom_level = 1.0
        self.rotation_angle = 0
        
        self.create_widgets()
        self.bind_keys()

    def create_widgets(self):
        # 1. Top Toolbar (Clean, dark gray)
        toolbar = tk.Frame(self, bg="#1f1f1f", height=50)
        toolbar.pack(fill="x", side="top")
        
        # Styles
        btn_config = {
            "bg": "#2d2d2d", "fg": "#e0e0e0", 
            "activebackground": "#3d3d3d", "activeforeground": "#ffffff",
            "bd": 0, "relief": "flat", "font": ("Segoe UI", 10),
            "padx": 15, "pady": 6, "cursor": "hand2"
        }

        # Open Button
        open_btn = tk.Button(toolbar, text="📂 Open", command=self.open_file, **btn_config)
        open_btn.pack(side="left", padx=10, pady=10)
        
        # Image Tools (Visible only in image mode, but packed here for simplicity)
        self.img_tools_frame = tk.Frame(toolbar, bg="#1f1f1f")
        self.img_tools_frame.pack(side="left", padx=20)
        
        tk.Button(self.img_tools_frame, text="⟳ Rotate", command=self.rotate_image, **btn_config).pack(side="left", padx=2)
        tk.Button(self.img_tools_frame, text="🔍 Reset Zoom", command=self.reset_zoom, **btn_config).pack(side="left", padx=2)

        # File Name Label
        self.status_label = tk.Label(toolbar, text="Welcome! Open a file to begin.", 
                                     bg="#1f1f1f", fg="#aaaaaa", font=("Segoe UI", 10, "italic"))
        self.status_label.pack(side="right", padx=20)

        # 2. Main Viewport
        self.viewport = tk.Frame(self, bg="#000000")
        self.viewport.pack(fill="both", expand=True)
        
        # We use a Canvas for images to allow smoother panning/zooming in future updates, 
        # but for now a Label centered is easier for Mixed Media (video frames).
        # To support video comfortably, Label is efficient enough for simple needs.
        self.media_label = tk.Label(self.viewport, bg="#000000")
        self.media_label.pack(expand=True, fill="both")

        # 3. Video Controls (Bottom Bar)
        self.video_controls = tk.Frame(self, bg="#1f1f1f", height=60, pady=10)
        
        # Playback Buttons
        btns_frame = tk.Frame(self.video_controls, bg="#1f1f1f")
        btns_frame.pack(side="left", padx=20)
        
        self.rewind_btn = tk.Button(btns_frame, text="⏪ -10s", command=lambda: self.seek_relative(-10), **btn_config)
        self.rewind_btn.pack(side="left", padx=2)
        
        self.play_btn = tk.Button(btns_frame, text="▶ Play", command=self.toggle_video, width=8, **btn_config)
        self.play_btn.config(bg="#007acc", fg="white", activebackground="#005f9e")
        self.play_btn.pack(side="left", padx=10)
        
        self.forward_btn = tk.Button(btns_frame, text="+10s ⏩", command=lambda: self.seek_relative(10), **btn_config)
        self.forward_btn.pack(side="left", padx=2)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_slider = ttk.Scale(self.video_controls, from_=0, to=100, variable=self.progress_var, orient="horizontal", command=self.seek_video_abs)
        self.progress_slider.pack(side="left", fill="x", expand=True, padx=20)
        
        # Initial Hide
        self.img_tools_frame.pack_forget()

    def bind_keys(self):
        self.bind("<space>", lambda e: self.toggle_video())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Left>", lambda e: self.seek_relative(-5))
        self.bind("<Right>", lambda e: self.seek_relative(5))
        self.bind("<MouseWheel>", self.on_zoom)

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
        self.cleanup_media()
        self.status_label.config(text=os.path.basename(path))

        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            self.mode = "image"
            self.switch_ui_mode("image")
            self.load_image(path)
        elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
            self.mode = "video"
            self.switch_ui_mode("video")
            self.load_video(path)
        else:
            messagebox.showerror("Error", "Unsupported file format")

    def cleanup_media(self):
        self.stop_video()
        self.media_label.config(image='')
        self.media_label.image = None
        self.current_image = None
        self.pil_image = None
        self.zoom_level = 1.0
        self.rotation_angle = 0

    def switch_ui_mode(self, mode):
        if mode == "image":
            self.video_controls.pack_forget()
            self.img_tools_frame.pack(side="left", padx=20)
        else:
            self.img_tools_frame.pack_forget()
            self.video_controls.pack(fill="x", side="bottom")

    # --- Image Logic ---
    def load_image(self, path):
        try:
            self.pil_image = Image.open(path)
            self.render_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def render_image(self):
        if not self.pil_image: return
        
        # Apply Rotation
        rotated = self.pil_image.rotate(-self.rotation_angle, expand=True) # Negative for clockwise visual feel usually
        
        # Apply Zoom
        w, h = rotated.size
        new_w = int(w * self.zoom_level)
        new_h = int(h * self.zoom_level)
        
        # Resize quality
        resized = rotated.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Check window bounds to avoid massive memory usage if zoom is crazy high, 
        # but for viewing normal photos let's just center it.
        # If image is larger than window, viewport handles clipping naturally.
        
        self.current_image = ImageTk.PhotoImage(resized)
        self.media_label.config(image=self.current_image)

    def on_zoom(self, event):
        if self.mode != "image": return
        if event.delta > 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level *= 0.9
        self.render_image()

    def rotate_image(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.render_image()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.rotation_angle = 0
        self.render_image()

    # --- Video Logic ---
    def load_video(self, path):
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open video file")
            return
        
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        self.progress_var.set(0)
        self.play_btn.config(text="▶ Play", bg="#007acc")
        
        # Display first frame
        self.show_current_frame()

    def show_current_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = frame.shape
                
                # Fit to window logic (simple)
                screen_w = self.viewport.winfo_width()
                screen_h = self.viewport.winfo_height()
                if screen_w < 10: screen_w = 800 # startup safety
                if screen_h < 10: screen_h = 600
                
                # Aspect Ratio
                aspect = w / h
                screen_aspect = screen_w / screen_h
                
                if aspect > screen_aspect:
                    new_w = screen_w
                    new_h = int(screen_w / aspect)
                else:
                    new_h = screen_h
                    new_w = int(screen_h * aspect)
                
                if new_w > 0 and new_h > 0:
                    frame = cv2.resize(frame, (new_w, new_h))
                
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.media_label.config(image=imgtk)
                self.media_label.image = imgtk
            return ret
        return False

    def toggle_video(self):
        if self.is_video_playing:
            self.stop_video_flag = True
            self.is_video_playing = False
            self.play_btn.config(text="▶ Play", bg="#007acc")
        else:
            if self.cap and self.cap.isOpened():
                self.is_video_playing = True
                self.stop_video_flag = False
                self.play_btn.config(text="⏸ Pause", bg="#e0a800")
                self.video_thread = threading.Thread(target=self.play_loop, daemon=True)
                self.video_thread.start()

    def play_loop(self):
        while not self.stop_video_flag and self.cap and self.cap.isOpened():
            start_time = time.time()
            
            # Read logic handles skipping frames if needed, but for simple player we just read
            ret, frame = self.cap.read()
            if not ret:
                # Loop video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # UI Update needs to be reasonably fast
            # We reuse the resize logic from show_current_frame but duplicate here to avoid self.cap.read() conflict
            # Wait! show_current_frame READS a frame. We already read "frame".
            # Let's just render the frame we hold.
            
            if frame is None: continue
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame_rgb.shape
            
            # Use fixed size if viewport size changes too fast to avoid jitter, 
            # but getting winfo is fast enough usually.
            screen_w = self.viewport.winfo_width()
            screen_h = self.viewport.winfo_height()
            if screen_w < 10: screen_w = 800 
            if screen_h < 10: screen_h = 600
            
            aspect = w / h
            if aspect > (screen_w / screen_h):
                new_w = screen_w
                new_h = int(screen_w / aspect)
            else:
                new_h = screen_h
                new_w = int(screen_h * aspect)
                
            frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)
            
            try:
                self.media_label.config(image=imgtk)
                self.media_label.image = imgtk
                
                # Update progress
                curr = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                self.progress_var.set((curr / self.total_frames) * 100)
            except:
                break

            elapsed = time.time() - start_time
            delay = max(0.001, (1.0/self.fps) - elapsed)
            time.sleep(delay)
            
        self.is_video_playing = False
        # If we exited loop without flag (e.g. error), reset btn
        try:
             self.play_btn.config(text="▶ Play", bg="#007acc")
        except: pass

    def seek_video_abs(self, value):
        if self.cap:
            target = int((float(value) / 100) * self.total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target)
            # If paused, update frame to show where we are
            if not self.is_video_playing:
                self.show_current_frame()

    def seek_relative(self, seconds):
        if self.cap:
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            frames_to_move = int(seconds * self.fps)
            new_frame = max(0, min(self.total_frames, current_frame + frames_to_move))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            if not self.is_video_playing:
                self.show_current_frame()

    def stop_video(self):
        self.stop_video_flag = True
        self.is_video_playing = False
        time.sleep(0.1)
        if self.cap:
            self.cap.release()
            self.cap = None

if __name__ == "__main__":
    app = MediaViewerApp()
    app.mainloop()
