
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from client_module import ClientManager
from settings_module import SettingsManager
from case_module import CaseManager

class LexGuardianApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_file = "config.json"
        self.load_config()
        
        self.title("LexGuardian - Advocate Case Assistant")
        self.geometry(self.window_size)
        
        self.apply_theme_colors()
        self.configure_styles()
        self.setup_layout()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.window_size = config.get("window_size", "1100x700")
                    self.theme = config.get("theme", "light")
                    return
            except Exception:
                pass
        self.window_size = "1100x700"
        self.theme = "light"

    def save_config_kv(self, key, value):
        config = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        config[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def apply_theme_colors(self):
        if self.theme == "dark":
            self.colors = {
                "bg_main": "#121212",
                "bg_sidebar": "#1F1F1F",
                "bg_card": "#252525",
                "fg_text": "#E0E0E0",
                "fg_sub": "#A0A0A0",
                "accent": "#1ABC9C",
                "border": "#333333"
            }
        else:
            self.colors = {
                "bg_main": "#ECF0F1",
                "bg_sidebar": "#2C3E50",
                "bg_card": "#FFFFFF",
                "fg_text": "#2C3E50",
                "fg_sub": "#7F8C8D",
                "accent": "#3498DB",
                "border": "#D5D8DC"
            }

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.save_config_kv("theme", self.theme)
        self.apply_theme_colors()
        self.configure_styles()
        # Refresh current view
        view_type = type(self.current_view)
        if view_type == ClientManager: self.show_clients()
        elif view_type == CaseManager: self.show_cases()
        elif view_type == SettingsManager: self.show_settings()
        else: self.show_dashboard()
        # Re-layout sidebar/main to apply new colors
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_layout()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg = self.colors["bg_card"]
        fg = self.colors["fg_text"]
        
        style.configure("Treeview", 
                        background=bg, 
                        foreground=fg, 
                        fieldbackground=bg, 
                        rowheight=25)
        style.map("Treeview", background=[('selected', self.colors["accent"])])
        
        style.configure("TNotebook", background=self.colors["bg_main"])
        style.configure("TNotebook.Tab", background=self.colors["bg_sidebar"], foreground="white", padding=[10, 2])
        style.map("TNotebook.Tab", background=[('selected', self.colors["accent"])])
        
        style.configure("TCombobox", fieldbackground=bg, background=bg, foreground=fg)

    def setup_layout(self):
        # Sidebar Navigation
        sidebar = tk.Frame(self, bg=self.colors["bg_sidebar"], width=200)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="LEX GUARDIAN", fg="white", bg=self.colors["bg_sidebar"], font=("Arial", 14, "bold"), pady=20).pack()

        nav_btns = [
            ("Dashboard", self.show_dashboard),
            ("Clients", self.show_clients),
            ("Cases", self.show_cases),
            ("Reminders", self.show_reminders),
            ("Settings", self.show_settings)
        ]

        for text, command in nav_btns:
            btn = tk.Button(sidebar, text=text, command=command, flat=True, 
                          bg="#34495E" if self.theme == "light" else "#2C2C2C", 
                          fg="white", activebackground=self.colors["accent"], 
                          anchor="w", padx=20, pady=10, relief="flat")
            btn.pack(fill="x", pady=1)

        # Theme Toggle at bottom of sidebar
        theme_btn_text = "☀️ Light Mode" if self.theme == "dark" else "🌙 Dark Mode"
        tk.Button(sidebar, text=theme_btn_text, command=self.toggle_theme, 
                  flat=True, bg="#1ABC9C", fg="white", font=("Arial", 9, "bold"), 
                  pady=10).pack(side="bottom", fill="x")

        # Main Content Area
        self.content_area = tk.Frame(self, bg=self.colors["bg_main"])
        self.content_area.pack(side="right", fill="both", expand=True)
        
        self.current_view = None
        self.show_dashboard()

    def clear_content(self):
        if self.current_view:
            self.current_view.destroy()

    def show_dashboard(self):
        self.clear_content()
        self.current_view = tk.Frame(self.content_area, bg=self.colors["bg_main"])
        self.current_view.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(self.current_view, text="Dashboard Overview", font=("Arial", 18, "bold"), 
                 bg=self.colors["bg_main"], fg=self.colors["fg_text"]).pack(anchor="w")
        
        # Summary Cards
        cards_frame = tk.Frame(self.current_view, bg=self.colors["bg_main"])
        cards_frame.pack(fill="x", pady=20)
        
        self.create_card(cards_frame, "Active Cases", "12", "#3498DB").grid(row=0, column=0, padx=10)
        self.create_card(cards_frame, "Hearings Today", "3", "#E67E22").grid(row=0, column=1, padx=10)
        self.create_card(cards_frame, "Pending Tasks", "5", "#E74C3C").grid(row=0, column=2, padx=10)

        # Disclaimer
        tk.Label(self.current_view, text="Safe Mode: AI assistance only. Advocate decides.", 
                 fg=self.colors["fg_sub"], bg=self.colors["bg_main"], font=("Arial", 9, "italic")).pack(side="bottom", pady=10)

    def create_card(self, parent, title, value, color):
        bg_color = self.colors["bg_card"]
        card = tk.Frame(parent, bg=bg_color, highlightbackground=color, highlightthickness=2, padx=20, pady=20)
        tk.Label(card, text=title, font=("Arial", 10), bg=bg_color, fg=self.colors["fg_sub"]).pack()
        tk.Label(card, text=value, font=("Arial", 20, "bold"), bg=bg_color, fg=color).pack()
        return card

    def show_clients(self):
        self.clear_content()
        self.current_view = ClientManager(self.content_area)
        self.current_view.pack(fill="both", expand=True)

    def show_cases(self):
        self.clear_content()
        self.current_view = CaseManager(self.content_area)
        self.current_view.pack(fill="both", expand=True)

    def show_reminders(self):
        self.clear_content()
        tk.Label(self.content_area, text="Reminders Module (In Development)", 
                 bg=self.colors["bg_main"], fg=self.colors["fg_text"], font=("Arial", 12)).pack(pady=50)

    def show_settings(self):
        self.clear_content()
        self.current_view = SettingsManager(self.content_area)
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = LexGuardianApp()
    app.mainloop()
