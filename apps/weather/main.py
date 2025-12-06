import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import threading

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Global Weather")
        self.geometry("500x700")
        self.configure(bg="#0f0f1a")
        self.resizable(False, False)
        
        # Styles
        self.fonts = {
            "header": ("Segoe UI", 28, "bold"),
            "sub": ("Segoe UI", 12),
            "temp": ("Segoe UI", 48, "bold"),
            "detail": ("Segoe UI", 14)
        }
        self.colors = {
            "bg": "#0f0f1a",
            "card": "#1c1c2e",
            "text": "#ffffff",
            "accent": "#4a90e2",
            "input_bg": "#2a2a40"
        }
        
        self.create_widgets()
        
        # Load Globe Image
        try:
            self.load_globe()
        except Exception as e:
            print(f"Error loading globe: {e}")

    def create_widgets(self):
        # Search Bar Frame
        search_frame = tk.Frame(self, bg=self.colors["bg"], pady=20)
        search_frame.pack(fill="x", padx=30)
        
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(search_frame, textvariable=self.city_var, font=("Segoe UI", 14), 
                                   bg=self.colors["input_bg"], fg="white", insertbackground="white", 
                                   relief="flat", justify="center")
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.city_entry.bind("<Return>", lambda e: self.search_weather())
        
        search_btn = tk.Button(search_frame, text="🔍", font=("Segoe UI", 12), 
                               bg=self.colors["accent"], fg="white", 
                               activebackground="#357abd", activeforeground="white",
                               relief="flat", command=self.search_weather, width=4)
        search_btn.pack(side="left", ipady=4)

        # Globe Container
        self.globe_frame = tk.Frame(self, bg=self.colors["bg"], height=250)
        self.globe_frame.pack(fill="x", pady=(10, 5))
        self.globe_label = tk.Label(self.globe_frame, bg=self.colors["bg"])
        self.globe_label.pack()

        # Suggested Cities
        suggestions_frame = tk.Frame(self, bg=self.colors["bg"])
        suggestions_frame.pack(fill="x", pady=5)
        
        cities = ["Abuja", "London", "California, US", "Beijing"]
        for city in cities:
            tk.Button(suggestions_frame, text=city.split(",")[0], 
                      font=("Segoe UI", 9), bg="#2d2d44", fg="white", bd=0, 
                      activebackground=self.colors["accent"], activeforeground="white",
                      command=lambda c=city: self.quick_search(c)
            ).pack(side="left", expand=True, padx=5, ipady=2, fill="x")

        # Content Area
        self.info_frame = tk.Frame(self, bg=self.colors["bg"])
        self.info_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Initial Placeholder
        self.msg_label = tk.Label(self.info_frame, text="Search for a city...", 
                                  font=self.fonts["sub"], bg=self.colors["bg"], fg="#8888aa")
        self.msg_label.pack(pady=20)
        
        # Weather Widgets (Hidden initially)
        self.city_label = tk.Label(self.info_frame, text="", font=self.fonts["header"], 
                                   bg=self.colors["bg"], fg=self.colors["text"])
        
        self.temp_label = tk.Label(self.info_frame, text="", font=self.fonts["temp"], 
                                   bg=self.colors["bg"], fg=self.colors["accent"])
        
        self.desc_label = tk.Label(self.info_frame, text="", font=self.fonts["sub"], 
                                   bg=self.colors["bg"], fg="#cccccc")
        
        # Grid for details
        self.details_frame = tk.Frame(self.info_frame, bg=self.colors["card"], padx=20, pady=20)
        
    def load_globe(self):
        # Load and resize globe
        img_path = "apps/weather/globe.png"
        pil_img = Image.open(img_path)
        # Resize to fit nicely
        pil_img.thumbnail((250, 250))
        self.globe_img = ImageTk.PhotoImage(pil_img)
        self.globe_label.config(image=self.globe_img)

    def quick_search(self, city_name):
        self.city_var.set(city_name)
        self.search_weather()

    def search_weather(self):
        city = self.city_var.get().strip()
        if not city: return
        
        self.msg_label.config(text=f"Searching for {city}...", fg=self.colors["accent"])
        self.msg_label.pack(pady=20) # Ensure visible if hidden
        self.city_label.pack_forget() # Hide old data
        self.temp_label.pack_forget()
        self.desc_label.pack_forget()
        self.details_frame.pack_forget()
        
        # Run in thread to prevent freezing
        threading.Thread(target=self.fetch_weather, args=(city,), daemon=True).start()

    def fetch_weather(self, city):
        try:
            # 1. Geocode
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url).json()
            
            if not geo_res.get("results"):
                self.update_ui_error("City not found.")
                return
                
            location = geo_res["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            name = location["name"]
            country = location.get("country", "")
            
            # 2. Weather
            # Getting current weather + temp/wind/humidity
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&temperature_unit=celsius&wind_speed_unit=kmh"
            w_res = requests.get(w_url).json()
            
            current = w_res.get("current", {})
            
            data = {
                "name": name,
                "country": country,
                "temp": current.get("temperature_2m"),
                "feels_like": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "wind": current.get("wind_speed_10m"),
                "code": current.get("weather_code")
            }
            
            self.after(0, self.update_ui_success, data)
            
        except Exception as e:
            self.after(0, self.update_ui_error, f"Connection error: {e}")

    def get_weather_desc(self, code):
        # WMO Weather interpretation codes (WW)
        # Simplified list
        if code == 0: return "Clear Sky ☀️"
        if code in [1, 2, 3]: return "Partly Cloudy ⛅"
        if code in [45, 48]: return "Foggy 🌫️"
        if code in [51, 53, 55]: return "Drizzle 🌧️"
        if code in [61, 63, 65]: return "Rain 🌧️"
        if code in [71, 73, 75]: return "Snow ❄️"
        if code in [95, 96, 99]: return "Thunderstorm ⚡"
        return "Unknown"

    def update_ui_success(self, data):
        self.msg_label.pack_forget()
        
        # Show main elements
        self.city_label.config(text=f"{data['name']}, {data['country']}")
        self.city_label.pack(pady=(10, 5))
        
        self.temp_label.config(text=f"{data['temp']}°C")
        self.temp_label.pack()
        
        condition = self.get_weather_desc(data['code'])
        self.desc_label.config(text=condition)
        self.desc_label.pack(pady=(0, 20))
        
        # Details Grid
        self.details_frame.pack(fill="x", pady=10)
        # Clear previous if any
        for widget in self.details_frame.winfo_children():
            widget.destroy()
            
        # Helper to make detail item
        def add_item(row, col, label, value):
            tk.Label(self.details_frame, text=label, font=("Segoe UI", 10), bg=self.colors["card"], fg="#aaaaaa").grid(row=row, column=col, padx=10, sticky="w")
            tk.Label(self.details_frame, text=value, font=("Segoe UI", 12, "bold"), bg=self.colors["card"], fg="white").grid(row=row+1, column=col, padx=10, pady=(0, 10), sticky="w")
        
        add_item(0, 0, "Feels Like", f"{data['feels_like']}°C")
        add_item(0, 1, "Humidity", f"{data['humidity']}%")
        add_item(0, 2, "Wind", f"{data['wind']} km/h")
        
        self.details_frame.grid_columnconfigure(0, weight=1)
        self.details_frame.grid_columnconfigure(1, weight=1)
        self.details_frame.grid_columnconfigure(2, weight=1)

    def update_ui_error(self, message):
        self.msg_label.config(text=message, fg="#ff5555")
        self.msg_label.pack(pady=20)
        self.city_label.pack_forget()
        self.temp_label.pack_forget()
        self.desc_label.pack_forget()
        self.details_frame.pack_forget()

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
