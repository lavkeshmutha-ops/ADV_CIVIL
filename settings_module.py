
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SettingsManager(tk.Frame):
    def __init__(self, parent):
        self.app = parent.master.master
        bg_color = self.app.colors["bg_main"]
        super().__init__(parent, bg=bg_color)
        self.config_file = "config.json"
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        colors = self.app.colors
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=colors["bg_main"])
        self.canvas.pack(fill="both", expand=True)
        
        # Apply gradient only in light mode for aesthetics, solid in dark
        if self.app.theme == "light":
            self.bind("<Configure>", self._draw_gradient)

        # Main Scrollable Container
        self.container = tk.Frame(self.canvas, bg=colors["bg_card"], padx=40, pady=40, relief="flat", highlightthickness=1, highlightbackground=colors["border"])
        self.container.place(relx=0.5, rely=0.5, anchor="center", width=600, height=550)

        # Header
        tk.Label(self.container, text="System Configuration", 
                 font=("Segoe UI", 20, "bold"), bg=colors["bg_card"], fg=colors["fg_text"]).pack(anchor="w", pady=(0, 5))
        
        tk.Label(self.container, text="Manage local database and display preferences", 
                 font=("Segoe UI", 10), bg=colors["bg_card"], fg=colors["fg_sub"]).pack(anchor="w", pady=(0, 30))

        # Database Section
        db_group = tk.LabelFrame(self.container, text=" DATABASE CONNECTION ", 
                                 font=("Segoe UI", 9, "bold"), bg=colors["bg_card"], fg=colors["accent"], 
                                 padx=20, pady=20, relief="flat", highlightthickness=1, highlightbackground=colors["border"])
        db_group.pack(fill="x", pady=10)

        tk.Label(db_group, text="MySQL Root Password", bg=colors["bg_card"], font=("Segoe UI", 10), fg=colors["fg_text"]).pack(anchor="w")
        self.ent_db_pass = tk.Entry(db_group, show="•", font=("Segoe UI", 11), 
                                   bg=colors["bg_main"], fg=colors["fg_text"], relief="flat", highlightthickness=1, highlightbackground=colors["border"], insertbackground=colors["fg_text"])
        self.ent_db_pass.pack(fill="x", pady=(5, 10), ipady=5)

        # UI Section
        ui_group = tk.LabelFrame(self.container, text=" INTERFACE PREFERENCES ", 
                                 font=("Segoe UI", 9, "bold"), bg=colors["bg_card"], fg=colors["accent"], 
                                 padx=20, pady=20, relief="flat", highlightthickness=1, highlightbackground=colors["border"])
        ui_group.pack(fill="x", pady=10)

        tk.Label(ui_group, text="Initial Launch Resolution", bg=colors["bg_card"], font=("Segoe UI", 10), fg=colors["fg_text"]).pack(anchor="w")
        self.combo_resolution = ttk.Combobox(ui_group, values=["1024x768", "1100x700", "1280x800", "1920x1080"], 
                                            state="readonly", font=("Segoe UI", 11))
        self.combo_resolution.set("1100x700")
        self.combo_resolution.pack(fill="x", pady=(5, 0))

        # Footer Actions
        btn_frame = tk.Frame(self.container, bg=colors["bg_card"])
        btn_frame.pack(fill="x", pady=(40, 0))

        tk.Button(btn_frame, text="Apply & Save", command=self.save_settings, 
                  bg=colors["accent"], fg="white", font=("Segoe UI", 11, "bold"), 
                  relief="flat", cursor="hand2", padx=30, pady=10).pack(side="right")

    def _draw_gradient(self, event=None):
        if self.app.theme == "dark": return
        self.canvas.delete("gradient")
        width, height = self.winfo_width(), self.winfo_height()
        (r1, g1, b1) = self.winfo_rgb("#ECF0F1")
        (r2, g2, b2) = self.winfo_rgb("#D7DBDD")
        r_ratio, g_ratio, b_ratio = (r2-r1)/height, (g2-g1)/height, (b2-b1)/height
        for i in range(0, height, 2):
            color = "#%04x%04x%04x" % (int(r1+r_ratio*i), int(g1+g_ratio*i), int(b1+b_ratio*i))
            self.canvas.create_rectangle(0, i, width, i + 2, tags="gradient", fill=color, outline=color)
        self.canvas.tag_lower("gradient")

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.ent_db_pass.delete(0, tk.END)
                    self.ent_db_pass.insert(0, config.get("db_password", "password"))
                    self.combo_resolution.set(config.get("window_size", "1100x700"))
            except Exception: pass

    def save_settings(self):
        config = {"db_password": self.ent_db_pass.get(), "window_size": self.combo_resolution.get(), "theme": self.app.theme}
        try:
            with open(self.config_file, 'w') as f: json.dump(config, f)
            messagebox.showinfo("Success", "Settings updated.")
        except Exception as e: messagebox.showerror("Error", str(e))
