import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
from PIL import Image, ImageTk

class MusicPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Neon Music Player")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # Init Pygame Mixer
        pygame.mixer.init()
        
        # State
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        
        # Colors
        self.bg_color = "#121212"
        self.accent_color = "#BB86FC"
        
        self.configure(bg=self.bg_color)
        
        self.create_bg()
        self.create_widgets()
        
    def create_bg(self):
        try:
            pil_img = Image.open("apps/music_player/bg.png")
            # Crop/Resize to fit 400x300 top half
            pil_img = pil_img.resize((400, 300), Image.Resampling.LANCZOS)
            self.album_art_img = ImageTk.PhotoImage(pil_img)
        except:
            self.album_art_img = None

    def create_widgets(self):
        # Album Art Area
        self.art_label = tk.Label(self, bg=self.bg_color, image=self.album_art_img)
        self.art_label.pack(side="top", fill="x")
        
        # Song Info
        self.song_label = tk.Label(self, text="No Song Playing", font=("Segoe UI", 12, "bold"),
                                   bg=self.bg_color, fg="white", wraplength=380)
        self.song_label.pack(pady=(15, 5))
        
        # Controls Frame
        controls_frame = tk.Frame(self, bg=self.bg_color)
        controls_frame.pack(pady=10)
        
        btn_config = {"bg": self.bg_color, "fg": "white", "bd": 0, "font": ("Segoe UI Emoji", 20), 
                      "activebackground": "#2a2a2a", "activeforeground": self.accent_color, "cursor": "hand2"}
        
        tk.Button(controls_frame, text="⏮", command=self.prev_song, **btn_config).pack(side="left", padx=10)
        self.play_btn = tk.Button(controls_frame, text="▶", command=self.toggle_play, **btn_config)
        self.play_btn.pack(side="left", padx=10)
        tk.Button(controls_frame, text="⏭", command=self.next_song, **btn_config).pack(side="left", padx=10)
        
        # Add Song Button
        tk.Button(self, text="+ Add Songs", command=self.add_songs, font=("Segoe UI", 10),
                  bg="#2a2a2a", fg="#cccccc", bd=0).pack(pady=5)
        
        # Playlist
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.playlist_box = tk.Listbox(list_frame, bg="#1e1e1e", fg="#dddddd", 
                                       selectbackground=self.accent_color, selectforeground="black",
                                       bd=0, highlightthickness=0, font=("Segoe UI", 10))
        self.playlist_box.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, command=self.playlist_box.yview)
        scrollbar.pack(side="right", fill="y")
        self.playlist_box.config(yscrollcommand=scrollbar.set)
        
        self.playlist_box.bind("<Double-Button-1>", self.play_selected)

    def add_songs(self):
        files = filedialog.askopenfilenames(title="Select Music", 
                                            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        for f in files:
            self.playlist.append(f)
            self.playlist_box.insert("end", os.path.basename(f))
            
    def play_selected(self, event=None):
        selection = self.playlist_box.curselection()
        if selection:
            self.current_index = selection[0]
            self.play_song()

    def play_song(self):
        if not self.playlist: return
        
        path = self.playlist[self.current_index]
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.play_btn.config(text="⏸", fg=self.accent_color)
            self.song_label.config(text=os.path.basename(path)[:-4]) # remove extension
            
            # Update selection UI
            self.playlist_box.selection_clear(0, "end")
            self.playlist_box.selection_set(self.current_index)
            self.playlist_box.activate(self.current_index)
            
        except Exception as e:
            print(f"Error playing file: {e}")

    def toggle_play(self):
        if not self.playlist: return
        
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.play_btn.config(text="⏸", fg=self.accent_color)
            else:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_btn.config(text="▶", fg="white")
        else:
            self.play_song()

    def next_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_song()

    def prev_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_song()

if __name__ == "__main__":
    app = MusicPlayerApp()
    app.mainloop()
