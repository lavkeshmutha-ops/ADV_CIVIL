
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import db
import os
import asyncio
import threading
import platform
import subprocess
from ai_service import AIService
from datetime import datetime

class CaseManager(tk.Frame):
    def __init__(self, parent):
        self.app = parent.master.master
        bg_color = self.app.colors["bg_main"]
        super().__init__(parent, bg=bg_color)
        self.ai_service = AIService()
        self.editing_timeline_id = None # Track if we are editing an existing record
        self.setup_ui()
        self.load_cases()

    def setup_ui(self):
        colors = self.app.colors
        # Top Form for Adding Cases
        form_frame = tk.LabelFrame(self, text=" Register New Case ", font=("Segoe UI", 10, "bold"), 
                                   bg=colors["bg_card"], fg=colors["accent"], padx=15, pady=15)
        form_frame.pack(fill="x", padx=20, pady=10)

        # Row 1
        tk.Label(form_frame, text="Client:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=0, column=0, sticky="w")
        self.combo_client = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_client.grid(row=0, column=1, padx=5, pady=5)
        self.load_clients_into_combo()

        tk.Label(form_frame, text="Case Number:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=0, column=2, sticky="w")
        self.ent_case_num = tk.Entry(form_frame, width=25, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_case_num.grid(row=0, column=3, padx=5, pady=5)

        # Row 2
        tk.Label(form_frame, text="Case Title:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=1, column=0, sticky="w")
        self.ent_title = tk.Entry(form_frame, width=33, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_title.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Court Name:", bg=colors["bg_card"], fg=colors["fg_text"]).grid(row=1, column=2, sticky="w")
        self.ent_court = tk.Entry(form_frame, width=25, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_court.grid(row=1, column=3, padx=5, pady=5)

        btn_save = tk.Button(form_frame, text="Add Case", command=self.save_case, bg="#27AE60", fg="white", font=("Segoe UI", 9, "bold"), padx=15)
        btn_save.grid(row=1, column=4, padx=10)

        # SEARCH AND FILTER TOOLBAR
        search_frame = tk.Frame(self, bg=colors["border"], padx=15, pady=8)
        search_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        tk.Label(search_frame, text="🔍 Search Case:", bg=colors["border"], fg=colors["fg_text"], font=("Segoe UI", 9, "bold")).pack(side="left")
        self.ent_search = tk.Entry(search_frame, width=30, bg=colors["bg_card"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", lambda e: self.load_cases())

        tk.Label(search_frame, text="Filter Status:", bg=colors["border"], fg=colors["fg_text"], font=("Segoe UI", 9, "bold")).pack(side="left", padx=(20, 5))
        self.combo_filter_status = ttk.Combobox(search_frame, values=["All", "Active", "Pending", "Closed"], state="readonly", width=12)
        self.combo_filter_status.set("All")
        self.combo_filter_status.pack(side="left")
        self.combo_filter_status.bind("<<ComboboxSelected>>", lambda e: self.load_cases())

        btn_reset = tk.Button(search_frame, text="Clear Filters", command=self.reset_filters, bg="#95A5A6", fg="white", font=("Segoe UI", 8))
        btn_reset.pack(side="right")

        # Main Content
        self.main_paned = tk.PanedWindow(self, orient="vertical", bg=colors["bg_main"], sashwidth=4)
        self.main_paned.pack(fill="both", expand=True, padx=20, pady=5)

        list_container = tk.Frame(self.main_paned, bg=colors["bg_card"])
        self.main_paned.add(list_container, height=200)

        status_toolbar = tk.Frame(list_container, bg=colors["bg_sidebar"], pady=5, padx=10)
        status_toolbar.pack(fill="x")
        
        tk.Label(status_toolbar, text="Update Selected Status:", bg=colors["bg_sidebar"], fg="white", font=("Segoe UI", 9)).pack(side="left")
        self.combo_status_update = ttk.Combobox(status_toolbar, values=["Active", "Closed", "Pending"], state="readonly", width=12)
        self.combo_status_update.pack(side="left", padx=5)
        
        self.btn_update_status = tk.Button(status_toolbar, text="Apply Status", command=self.update_case_status, bg="#F39C12", fg="white", font=("Segoe UI", 8, "bold"), state="disabled")
        self.btn_update_status.pack(side="left", padx=5)

        columns = ("ID", "Case No", "Title", "Client", "Court", "Status")
        self.tree = ttk.Treeview(list_container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_case_select)

        self.tabs = ttk.Notebook(self.main_paned)
        self.main_paned.add(self.tabs, height=450)

        self.timeline_tab = tk.Frame(self.tabs, bg=colors["bg_card"])
        self.tabs.add(self.timeline_tab, text=" Case Timeline & AI ")
        self.setup_timeline_ui()

        self.doc_tab = tk.Frame(self.tabs, bg=colors["bg_card"])
        self.tabs.add(self.doc_tab, text=" Documents ")
        self.setup_documents_ui()

    def setup_timeline_ui(self):
        colors = self.app.colors
        tl_paned = tk.PanedWindow(self.timeline_tab, orient="horizontal", bg=colors["border"], sashwidth=4)
        tl_paned.pack(fill="both", expand=True)

        tl_form = tk.Frame(tl_paned, bg=colors["bg_card"], padx=10, pady=10)
        tl_paned.add(tl_form, width=350)

        self.tl_header_label = tk.Label(tl_form, text="Add Hearing Record", font=("Segoe UI", 11, "bold"), bg=colors["bg_card"], fg=colors["accent"])
        self.tl_header_label.pack(anchor="w", pady=(0,10))
        
        tk.Label(tl_form, text="Hearing Date:", bg=colors["bg_card"], fg=colors["fg_text"]).pack(anchor="w")
        self.ent_tl_date = tk.Entry(tl_form, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"])
        self.ent_tl_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_tl_date.pack(fill="x", pady=(0,10))

        tk.Label(tl_form, text="Proceedings:", bg=colors["bg_card"], fg=colors["fg_text"]).pack(anchor="w")
        self.txt_tl_proceedings = tk.Text(tl_form, height=5, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"], borderwidth=0)
        self.txt_tl_proceedings.pack(fill="x", pady=(0,10))

        tk.Label(tl_form, text="Order/Next Action:", bg=colors["bg_card"], fg=colors["fg_text"]).pack(anchor="w")
        self.txt_tl_order = tk.Text(tl_form, height=3, bg=colors["bg_main"], fg=colors["fg_text"], insertbackground=colors["fg_text"], borderwidth=0)
        self.txt_tl_order.pack(fill="x", pady=(0,10))

        btn_save_tl = tk.Button(tl_form, text="Save Hearing Record", command=self.save_timeline_entry, bg="#27AE60", fg="white", font=("Segoe UI", 9, "bold"))
        btn_save_tl.pack(fill="x", pady=5)
        
        self.btn_tl_clear_form = tk.Button(tl_form, text="Clear Form", command=self.clear_timeline_form, bg="#95A5A6", fg="white", font=("Segoe UI", 8))
        self.btn_tl_clear_form.pack(fill="x", pady=2)

        tl_list_frame = tk.Frame(tl_paned, bg=colors["bg_card"])
        tl_paned.add(tl_list_frame)

        tl_toolbar = tk.Frame(tl_list_frame, bg=colors["bg_sidebar"], padx=10, pady=5)
        tl_toolbar.pack(fill="x")

        self.btn_ai_summarize = tk.Button(tl_toolbar, text="✨ AI Summarize", command=self.trigger_ai_summarization, bg="#9B59B6", fg="white", font=("Segoe UI", 8, "bold"), state="disabled")
        self.btn_ai_summarize.pack(side="left", padx=5)

        self.btn_ai_clear = tk.Button(tl_toolbar, text="🧹 Clear AI", command=self.clear_ai_summary, bg="#BDC3C7", fg="#2C3E50", font=("Segoe UI", 8), state="disabled")
        self.btn_ai_clear.pack(side="left", padx=5)

        self.btn_tl_delete = tk.Button(tl_toolbar, text="🗑 Delete", command=self.delete_timeline_entry, bg="#E74C3C", fg="white", font=("Segoe UI", 8), state="disabled")
        self.btn_tl_delete.pack(side="right", padx=5)

        cols = ("ID", "Date", "Proceedings", "Order", "AI Summary")
        self.timeline_tree = ttk.Treeview(tl_list_frame, columns=cols, show="headings")
        for col in cols: self.timeline_tree.heading(col, text=col)
        self.timeline_tree.column("ID", width=40)
        self.timeline_tree.pack(fill="both", expand=True)
        self.timeline_tree.bind("<<TreeviewSelect>>", self.on_timeline_select)
        self.timeline_tree.bind("<Double-1>", self.on_timeline_double_click)

    def setup_documents_ui(self):
        colors = self.app.colors
        toolbar = tk.Frame(self.doc_tab, bg=colors["bg_sidebar"], padx=10, pady=5)
        toolbar.pack(fill="x")
        
        self.btn_upload = tk.Button(toolbar, text="+ Upload", command=self.upload_document, bg="#3498DB", fg="white", font=("Segoe UI", 8, "bold"), state="disabled")
        self.btn_upload.pack(side="left", padx=5)

        self.btn_open_file = tk.Button(toolbar, text="📂 Open", command=self.open_document_file, bg="#1ABC9C", fg="white", font=("Segoe UI", 8, "bold"), state="disabled")
        self.btn_open_file.pack(side="left", padx=5)

        self.doc_tree = ttk.Treeview(self.doc_tab, columns=("ID", "Filename", "Path", "Date"), show="headings")
        for col in ("ID", "Filename", "Path", "Date"): self.doc_tree.heading(col, text=col)
        self.doc_tree.pack(fill="both", expand=True)
        self.doc_tree.bind("<<TreeviewSelect>>", self.on_doc_select)

    def reset_filters(self):
        self.ent_search.delete(0, tk.END)
        self.combo_filter_status.set("All")
        self.load_cases()

    def clear_timeline_form(self):
        self.editing_timeline_id = None
        self.tl_header_label.config(text="Add Hearing Record")
        self.ent_tl_date.delete(0, tk.END)
        self.ent_tl_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.txt_tl_proceedings.delete("1.0", tk.END)
        self.txt_tl_order.delete("1.0", tk.END)

    def on_timeline_double_click(self, event):
        selected = self.timeline_tree.selection()
        if not selected: return
        item = self.timeline_tree.item(selected[0])
        vals = item['values']
        
        self.editing_timeline_id = vals[0]
        self.tl_header_label.config(text=f"Editing Hearing Record #{self.editing_timeline_id}")
        
        self.ent_tl_date.delete(0, tk.END)
        self.ent_tl_date.insert(0, vals[1])
        
        self.txt_tl_proceedings.delete("1.0", tk.END)
        self.txt_tl_proceedings.insert("1.0", vals[2])
        
        self.txt_tl_order.delete("1.0", tk.END)
        self.txt_tl_order.insert("1.0", vals[3])

    def open_document_file(self):
        selected = self.doc_tree.selection()
        if not selected: return
        file_path = self.doc_tree.item(selected[0])['values'][2]
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", "The file no longer exists at this location.")
            return
        try:
            if platform.system() == 'Windows': os.startfile(file_path)
            elif platform.system() == 'Darwin': subprocess.call(('open', file_path))
            else: subprocess.call(('xdg-open', file_path))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_clients_into_combo(self):
        cursor = db.get_cursor()
        if cursor:
            cursor.execute("SELECT id, full_name FROM clients")
            self.clients = cursor.fetchall()
            self.combo_client['values'] = [f"{c['id']} - {c['full_name']}" for c in self.clients]

    def save_case(self):
        client_data = self.combo_client.get()
        case_num = self.ent_case_num.get()
        title = self.ent_title.get()
        court = self.ent_court.get()
        if not (client_data and case_num and title):
            messagebox.showwarning("Incomplete", "Please fill required fields.")
            return
        client_id = client_data.split(" - ")[0]
        cursor = db.get_cursor()
        if cursor:
            try:
                cursor.execute("INSERT INTO cases (client_id, case_number, title, court_name) VALUES (%s, %s, %s, %s)", (client_id, case_num, title, court))
                db.commit()
                self.load_cases()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_cases(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        search_term = self.ent_search.get().strip()
        status_filter = self.combo_filter_status.get()
        cursor = db.get_cursor()
        if cursor:
            query = "SELECT cases.id, cases.case_number, cases.title, clients.full_name, cases.court_name, cases.status FROM cases JOIN clients ON cases.client_id = clients.id WHERE (cases.case_number LIKE %s OR cases.title LIKE %s)"
            params = [f"%{search_term}%", f"%{search_term}%"]
            if status_filter != "All":
                query += " AND cases.status = %s"
                params.append(status_filter)
            query += " ORDER BY cases.id DESC"
            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=(row['id'], row['case_number'], row['title'], row['full_name'], row['court_name'], row['status']))

    def on_case_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.btn_upload.config(state="normal")
            self.btn_update_status.config(state="normal")
            case_id = self.tree.item(selected[0])['values'][0]
            self.load_documents(case_id)
            self.load_timeline(case_id)

    def on_timeline_select(self, event):
        selected = self.timeline_tree.selection()
        state = "normal" if selected else "disabled"
        self.btn_ai_summarize.config(state=state)
        self.btn_ai_clear.config(state=state)
        self.btn_tl_delete.config(state=state)

    def on_doc_select(self, event):
        self.btn_open_file.config(state="normal" if self.doc_tree.selection() else "disabled")

    def save_timeline_entry(self):
        case_sel = self.tree.selection()
        if not case_sel: 
            messagebox.showwarning("No Case", "Please select a case first.")
            return
            
        case_id = self.tree.item(case_sel[0])['values'][0]
        cursor = db.get_cursor()
        if not cursor: return
        
        proc_text = self.txt_tl_proceedings.get("1.0", tk.END).strip()
        order_text = self.txt_tl_order.get("1.0", tk.END).strip()
        date_text = self.ent_tl_date.get()
        
        try:
            should_auto_ai = False
            target_id = self.editing_timeline_id
            
            if self.editing_timeline_id:
                # Check if an AI summary exists before updating
                cursor.execute("SELECT ai_summary FROM case_timeline WHERE id = %s", (self.editing_timeline_id,))
                row = cursor.fetchone()
                if row and row['ai_summary'] and row['ai_summary'] != "---":
                    should_auto_ai = True
                
                cursor.execute("UPDATE case_timeline SET hearing_date=%s, proceedings=%s, order_summary=%s WHERE id=%s", 
                               (date_text, proc_text, order_text, self.editing_timeline_id))
            else:
                cursor.execute("INSERT INTO case_timeline (case_id, hearing_date, proceedings, order_summary) VALUES (%s, %s, %s, %s)", 
                               (case_id, date_text, proc_text, order_text))
                target_id = cursor.lastrowid
                
            db.commit()
            self.load_timeline(case_id)
            
            # Auto trigger AI if it was an edit with an existing summary
            if should_auto_ai:
                self.trigger_ai_summarization(manual_timeline_id=target_id, manual_proc=proc_text)
                
            self.clear_timeline_form()
            messagebox.showinfo("Success", "Hearing record saved.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_timeline_entry(self):
        selected = self.timeline_tree.selection()
        if not selected: return
        tl_id = self.timeline_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete this record?"):
            cursor = db.get_cursor()
            if cursor:
                cursor.execute("DELETE FROM case_timeline WHERE id = %s", (tl_id,))
                db.commit()
                self.load_timeline(self.tree.item(self.tree.selection()[0])['values'][0])

    def load_timeline(self, case_id):
        for i in self.timeline_tree.get_children(): self.timeline_tree.delete(i)
        cursor = db.get_cursor()
        if cursor:
            cursor.execute("SELECT id, hearing_date, proceedings, order_summary, ai_summary FROM case_timeline WHERE case_id = %s ORDER BY hearing_date DESC", (case_id,))
            for row in cursor.fetchall():
                self.timeline_tree.insert("", "end", values=(row['id'], row['hearing_date'], row['proceedings'], row['order_summary'], row['ai_summary'] or "---"))

    def trigger_ai_summarization(self, manual_timeline_id=None, manual_proc=None):
        if manual_timeline_id and manual_proc:
            timeline_id = manual_timeline_id
            proceedings = manual_proc
            is_auto = True
        else:
            selected = self.timeline_tree.selection()
            if not selected: return
            item = self.timeline_tree.item(selected[0])
            timeline_id = item['values'][0]
            proceedings = item['values'][2]
            is_auto = False

        status_text = "⌛ Auto-Updating..." if is_auto else "⌛ AI..."
        self.btn_ai_summarize.config(state="disabled", text=status_text)
        
        def run_ai():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            summary = loop.run_until_complete(self.ai_service.summarize_timeline(proceedings))
            self.after(0, lambda: self.save_ai_summary(timeline_id, summary))
        
        threading.Thread(target=run_ai, daemon=True).start()

    def save_ai_summary(self, timeline_id, summary):
        cursor = db.get_cursor()
        if cursor:
            cursor.execute("UPDATE case_timeline SET ai_summary = %s WHERE id = %s", (summary, timeline_id))
            db.commit()
            case_sel = self.tree.selection()
            if case_sel:
                self.load_timeline(self.tree.item(case_sel[0])['values'][0])
        self.btn_ai_summarize.config(state="normal", text="✨ AI Summarize")

    def clear_ai_summary(self):
        selected = self.timeline_tree.selection()
        if selected:
            tl_id = self.timeline_tree.item(selected[0])['values'][0]
            cursor = db.get_cursor()
            if cursor:
                cursor.execute("UPDATE case_timeline SET ai_summary = NULL WHERE id = %s", (tl_id,))
                db.commit()
                self.load_timeline(self.tree.item(self.tree.selection()[0])['values'][0])

    def update_case_status(self):
        selected = self.tree.selection()
        if not selected: return
        cursor = db.get_cursor()
        if cursor:
            cursor.execute("UPDATE cases SET status = %s WHERE id = %s", (self.combo_status_update.get(), self.tree.item(selected[0])['values'][0]))
            db.commit()
            self.load_cases()

    def upload_document(self):
        selected = self.tree.selection()
        if not selected: return
        file_path = filedialog.askopenfilename()
        if file_path:
            cursor = db.get_cursor()
            if cursor:
                cursor.execute("INSERT INTO documents (case_id, file_name, file_path) VALUES (%s, %s, %s)", 
                               (self.tree.item(selected[0])['values'][0], os.path.basename(file_path), file_path))
                db.commit()
                self.load_documents(self.tree.item(selected[0])['values'][0])

    def load_documents(self, case_id):
        for i in self.doc_tree.get_children(): self.doc_tree.delete(i)
        cursor = db.get_cursor()
        if cursor:
            cursor.execute("SELECT id, file_name, file_path, upload_date FROM documents WHERE case_id = %s", (case_id,))
            for row in cursor.fetchall():
                self.doc_tree.insert("", "end", values=(row['id'], row['file_name'], row['file_path'], row['upload_date']))
