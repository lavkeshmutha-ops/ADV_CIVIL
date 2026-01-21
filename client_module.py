
import tkinter as tk
from tkinter import ttk, messagebox
from database import db

class ClientManager(tk.Frame):
    def __init__(self, parent):
        self.app = parent.master.master # Access LexGuardianApp instance
        bg_color = self.app.colors["bg_main"]
        super().__init__(parent, bg=bg_color)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        colors = self.app.colors
        # Form Section
        form_frame = tk.LabelFrame(self, text=" Add New Client ", font=("Segoe UI", 10, "bold"), 
                                   padx=10, pady=10, bg=colors["bg_card"], fg=colors["accent"])
        form_frame.pack(side="top", fill="x", padx=20, pady=10)

        tk.Label(form_frame, text="Full Name:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=0, column=0, sticky="w")
        self.ent_name = tk.Entry(form_frame, width=30, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_name.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Phone:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=0, column=2, sticky="w")
        self.ent_phone = tk.Entry(form_frame, width=20, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_phone.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(form_frame, text="Email:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=1, column=0, sticky="w")
        self.ent_email = tk.Entry(form_frame, width=30, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_email.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(form_frame, text="Address:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=1, column=2, sticky="w")
        self.ent_address = tk.Entry(form_frame, width=20, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_address.grid(row=1, column=3, padx=5, pady=2)

        btn_save = tk.Button(form_frame, text="Save Client", command=self.save_client, bg="#27AE60", fg="white", padx=15, font=("Segoe UI", 9, "bold"))
        btn_save.grid(row=2, column=1, pady=10, sticky="e")

        # Action Buttons Section
        action_frame = tk.Frame(self, bg=colors["bg_main"])
        action_frame.pack(side="top", fill="x", padx=20)
        
        btn_delete = tk.Button(action_frame, text="Delete Selected Client", command=self.delete_client, bg="#E74C3C", fg="white", padx=10, font=("Segoe UI", 8))
        btn_delete.pack(side="left", pady=5)

        # List Section
        list_frame = tk.Frame(self, bg=colors["bg_card"])
        list_frame.pack(side="bottom", fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Name", "Phone", "Email", "Address")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def save_client(self):
        name = self.ent_name.get()
        phone = self.ent_phone.get()
        email = self.ent_email.get()
        address = self.ent_address.get()

        if not name:
            messagebox.showerror("Error", "Name is required")
            return

        cursor = db.get_cursor()
        if cursor:
            query = "INSERT INTO clients (full_name, phone, email, address) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, phone, email, address))
            db.commit()
            
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Client added successfully")

    def delete_client(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a client to delete.")
            return

        client_values = self.tree.item(selected_item)['values']
        client_id = client_values[0]
        client_name = client_values[1]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete client '{client_name}'?\nThis will also delete all associated cases.")
        
        if confirm:
            cursor = db.get_cursor()
            if cursor:
                try:
                    cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
                    db.commit()
                    self.load_data()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = db.get_cursor()
        if cursor:
            cursor.execute("SELECT * FROM clients ORDER BY id DESC")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=(row['id'], row['full_name'], row['phone'], row['email'], row['address']))

    def clear_fields(self):
        self.ent_name.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_address.delete(0, tk.END)
