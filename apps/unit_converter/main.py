import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

class UnitConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unit Converter")
        self.geometry("450x550")
        
        # Color Palette
        self.colors = {
            "bg": "#1e1e1e",
            "panel": "#252526",
            "fg": "#e0e0e0",
            "accent": "#007acc",
            "accent_text": "#ffffff",
            "input_bg": "#3c3c3c",
            "input_fg": "#ffffff"
        }
        
        self.configure(bg=self.colors["bg"])
        
        # Fonts
        self.header_font = ("Segoe UI", 20, "bold")
        self.label_font = ("Segoe UI", 10)
        self.input_font = ("Segoe UI", 14)
        self.result_font = ("Segoe UI", 24, "bold")

        # Conversion Data
        # Format: Category -> { Unit: Factor_to_Base_Unit }
        # Length Base: Meter
        # Weight Base: Gram
        self.conversions = {
            "Length": {
                "Meter": 1.0,
                "Kilometer": 1000.0,
                "Centimeter": 0.01,
                "Millimeter": 0.001,
                "Mile": 1609.34,
                "Yard": 0.9144,
                "Foot": 0.3048,
                "Inch": 0.0254
            },
            "Weight": {
                "Kilogram": 1000.0,
                "Gram": 1.0,
                "Milligram": 0.001,
                "Pound": 453.592,
                "Ounce": 28.3495,
                "Ton (Metric)": 1000000.0
            },
            "Temperature": {
                "Celsius": "C",
                "Fahrenheit": "F",
                "Kelvin": "K"
            }
        }
        
        self.create_widgets()
        
        # Set defaults
        self.category_var.set("Length")
        self.update_units()
        self.amount_var.set("1")
        self.convert()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg=self.colors["bg"], pady=20)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="Converter", font=self.header_font, 
                 bg=self.colors["bg"], fg=self.colors["fg"]).pack()

        # Main Content Frame
        main_frame = tk.Frame(self, bg=self.colors["bg"], padx=30)
        main_frame.pack(fill="both", expand=True)

        # Category Selection
        tk.Label(main_frame, text="CATEGORY", font=self.label_font, 
                 bg=self.colors["bg"], fg=self.colors["accent"]).pack(anchor="w", pady=(0, 5))
        
        self.category_var = tk.StringVar()
        self.category_cb = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                        values=list(self.conversions.keys()), 
                                        state="readonly", font=("Segoe UI", 12))
        self.category_cb.pack(fill="x", pady=(0, 20), ipady=4)
        self.category_cb.bind("<<ComboboxSelected>>", self.update_units)

        # Input Area
        tk.Label(main_frame, text="VALUE", font=self.label_font, 
                 bg=self.colors["bg"], fg=self.colors["accent"]).pack(anchor="w", pady=(0, 5))
        
        self.amount_var = tk.StringVar()
        self.amount_var.trace("w", lambda *args: self.convert())
        
        self.amount_entry = tk.Entry(main_frame, textvariable=self.amount_var, font=self.input_font,
                                     bg=self.colors["input_bg"], fg=self.colors["input_fg"], 
                                     relief="flat", insertbackground="white")
        self.amount_entry.pack(fill="x", pady=(0, 20), ipady=8)

        # Units Row
        units_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        units_frame.pack(fill="x", pady=(0, 20))
        
        # From Unit
        from_frame = tk.Frame(units_frame, bg=self.colors["bg"])
        from_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Label(from_frame, text="FROM", font=self.label_font, 
                 bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w")
        
        self.from_unit_var = tk.StringVar()
        self.from_menu = ttk.Combobox(from_frame, textvariable=self.from_unit_var, state="readonly")
        self.from_menu.pack(fill="x", ipady=2)
        self.from_menu.bind("<<ComboboxSelected>>", lambda e: self.convert())

        # Swap Button
        swap_btn = tk.Button(units_frame, text="⇄", font=("Arial", 14), 
                             bg=self.colors["bg"], fg=self.colors["accent"], bd=0, 
                             activebackground=self.colors["bg"], activeforeground="white",
                             cursor="hand2", command=self.swap_units)
        swap_btn.pack(side="left", padx=5, pady=(15, 0))

        # To Unit
        to_frame = tk.Frame(units_frame, bg=self.colors["bg"])
        to_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        tk.Label(to_frame, text="TO", font=self.label_font, 
                 bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w")
        
        self.to_unit_var = tk.StringVar()
        self.to_menu = ttk.Combobox(to_frame, textvariable=self.to_unit_var, state="readonly")
        self.to_menu.pack(fill="x", ipady=2)
        self.to_menu.bind("<<ComboboxSelected>>", lambda e: self.convert())

        # Result Display with container for visual separation
        result_container = tk.Frame(main_frame, bg=self.colors["panel"], pady=20, padx=10)
        result_container.pack(fill="x", pady=20)
        
        self.result_var = tk.StringVar()
        self.result_var.set("---")
        
        self.result_label = tk.Label(result_container, textvariable=self.result_var, 
                                     font=self.result_font, bg=self.colors["panel"], fg=self.colors["accent"])
        self.result_label.pack()
        
        self.unit_label = tk.Label(result_container, text="", font=("Segoe UI", 12),
                                   bg=self.colors["panel"], fg=self.colors["fg"])
        self.unit_label.pack()

    def update_units(self, event=None):
        category = self.category_var.get()
        units = list(self.conversions[category].keys())
        
        self.from_menu['values'] = units
        self.to_menu['values'] = units
        
        if units:
            self.from_unit_var.set(units[0])
            self.to_unit_var.set(units[1] if len(units) > 1 else units[0])
            
        self.convert()

    def swap_units(self):
        src = self.from_unit_var.get()
        dst = self.to_unit_var.get()
        self.from_unit_var.set(dst)
        self.to_unit_var.set(src)
        self.convert()

    def convert(self):
        try:
            val_str = self.amount_var.get()
            if not val_str:
                self.result_var.set("---")
                self.unit_label.config(text="")
                return

            val = float(val_str)
            category = self.category_var.get()
            from_u = self.from_unit_var.get()
            to_u = self.to_unit_var.get()
            
            result = 0.0
            
            if category == "Temperature":
                result = self.convert_temp(val, from_u, to_u)
            else:
                # Based on base unit factors
                factors = self.conversions[category]
                # Convert to base
                base_val = val * factors[from_u]
                # Convert from base to target
                result = base_val / factors[to_u]
            
            # Formatting: remove trailing zeros if int, else 4 decimals
            if result.is_integer():
                res_Text = f"{int(result)}"
            else:
                res_Text = f"{result:.4f}"
                
            self.result_var.set(res_Text)
            self.unit_label.config(text=to_u)
            
        except ValueError:
            self.result_var.set("...")
    
    def convert_temp(self, val, from_u, to_u):
        if from_u == to_u:
            return val
        
        # Convert to Celsius first
        celsius = 0.0
        if from_u == "Celsius":
            celsius = val
        elif from_u == "Fahrenheit":
            celsius = (val - 32) * 5/9
        elif from_u == "Kelvin":
            celsius = val - 273.15
            
        # Convert Celsius to Target
        if to_u == "Celsius":
            return celsius
        elif to_u == "Fahrenheit":
            return (celsius * 9/5) + 32
        elif to_u == "Kelvin":
            return celsius + 273.15
        
        return 0.0

if __name__ == "__main__":
    app = UnitConverterApp()
    app.mainloop()
