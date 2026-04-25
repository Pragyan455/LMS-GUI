import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class LMS_App:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Team 8")
        self.root.geometry("1000x900")
        
        # Database file name per your schema
        self.db_name = 'LMS.db' 

        self.style = ttk.Style()
        self.style.configure("TLabel", padding=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tabs organized by Requirements
        self.setup_checkout_tab()  # Req 1
        self.setup_borrower_tab()  # Req 2
        self.setup_book_tab()      # Req 3
        self.setup_reports_tab()   # Req 4 & 5
        self.setup_finance_tab()   # Req 6a & 6b

    def run_query(self, query, params=(), commit=False):
        try:
            conn = sqlite3.connect(self.db_name)
            curr = conn.cursor()
            curr.execute(query, params)
            if commit:
                conn.commit()
                res = curr.lastrowid
            else:
                res = curr.fetchall()
            conn.close()
            return res
        except Exception as e:
            messagebox.showerror("Database Error", f"SQL Error: {str(e)}")
            return None

    def create_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        return tree

    # --- Schema-Specific Helpers ---
    def get_publisher_names(self):
        # Updated to match column: publisher_name
        res = self.run_query("SELECT publisher_name FROM PUBLISHER")
        return [row[0] for row in res] if res else []

    def get_book_ids(self):
        # Updated to match column: book_id
        res = self.run_query("SELECT book_id FROM BOOK")
        return [row[0] for row in res] if res else []

    # --- REQ 1: Checkout ---
    def setup_checkout_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Checkouts")
        
        input_frame = tk.Frame(tab)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Book ID:").grid(row=0, column=0, sticky='e')
        self.bid_cb = ttk.Combobox(input_frame, values=self.get_book_ids())
        self.bid_cb.grid(row=0, column=1, pady=5)
        tk.Button(input_frame, text="🔄", command=lambda: self.bid_cb.config(values=self.get_book_ids())).grid(row=0, column=2, padx=5)

        tk.Label(input_frame, text="Branch ID:").grid(row=1, column=0, sticky='e')
        brid = tk.Entry(input_frame); brid.grid(row=1, column=1, pady=5)

        tk.Label(input_frame, text="Card No:").grid(row=2, column=0, sticky='e')
        cno = tk.Entry(input_frame); cno.grid(row=2, column=1, pady=5)

        tree = self.create_tree(tab, ("Book ID", "Branch ID", "Copies Available"))
        tree.pack(pady=10)

        def action():
            book_id = self.bid_cb.get()
            branch_id = brid.get()
            card = cno.get()
            
            if not book_id or not branch_id or not card:
                messagebox.showwarning("Input Error", "All fields are required.")
                return

            today = datetime.now().strftime('%Y-%m-%d')
            # Updated to match table BOOK_LOANS columns
            q = "INSERT INTO BOOK_LOANS (book_id, branch_id, card_no, date_out, due_date) VALUES (?, ?, ?, ?, ?)"
            self.run_query(q, (book_id, branch_id, card, today, '2026-05-30'), commit=True)
            
            # Fetch updated counts from BOOK_COPIES
            res = self.run_query("SELECT book_id, branch_id, no_of_copies FROM BOOK_COPIES WHERE book_id=?", (book_id,))
            for item in tree.get_children(): tree.delete(item)
            if res:
                for row in res: tree.insert("", "end", values=row)
            messagebox.showinfo("Success", "Checkout successful.")

        tk.Button(tab, text="Submit Checkout", command=action, bg="#4CAF50", fg="white", font=('Arial', 10, 'bold')).pack(pady=10)

    # --- REQ 2: New Borrower ---
    def setup_borrower_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Borrowers")
        
        tk.Label(tab, text="Add New Borrower", font=('Arial', 12, 'bold')).pack(pady=10)
        tk.Label(tab, text="Name:").pack(); name = tk.Entry(tab); name.pack()
        tk.Label(tab, text="Address:").pack(); addr = tk.Entry(tab); addr.pack()
        tk.Label(tab, text="Phone:").pack(); ph = tk.Entry(tab); ph.pack()

        def action():
            # Assuming BORROWER table columns: name, address, phone
            q = "INSERT INTO BORROWER (name, address, phone) VALUES (?, ?, ?)"
            card_no = self.run_query(q, (name.get(), addr.get(), ph.get()), commit=True)
            messagebox.showinfo("Success", f"Borrower registered. Card No: {card_no}")

        tk.Button(tab, text="Register", command=action, bg="#2196F3", fg="white").pack(pady=20)

    # --- REQ 3: Add Books ---
    def setup_book_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add Books")
        
        tk.Label(tab, text="Global Book Entry", font=('Arial', 12, 'bold')).pack(pady=10)
        tk.Label(tab, text="Title:").pack(); title = tk.Entry(tab); title.pack()
        
        tk.Label(tab, text="Select Publisher:").pack()
        self.pub_cb = ttk.Combobox(tab, values=self.get_publisher_names())
        self.pub_cb.pack()
        tk.Button(tab, text="Refresh Publishers", command=lambda: self.pub_cb.config(values=self.get_publisher_names())).pack(pady=2)
        
        tk.Label(tab, text="Author Name:").pack(); auth = tk.Entry(tab); auth.pack()

        def action():
            t = title.get()
            p = self.pub_cb.get()
            a = auth.get()
            
            if not t or not p:
                messagebox.showwarning("Input Error", "Title and Publisher are required.")
                return
                
            # INSERT into BOOK (columns: title, book_publisher)
            bid = self.run_query("INSERT INTO BOOK (title, book_publisher) VALUES (?, ?)", (t, p), commit=True)
            # INSERT into BOOK_AUTHORS (columns: book_id, author_name)
            self.run_query("INSERT INTO BOOK_AUTHORS (book_id, author_name) VALUES (?, ?)", (bid, a), commit=True)
            
            # Seed copies to branches (Assumes branch IDs 1-5 exist)
            for i in range(1, 6):
                self.run_query("INSERT INTO BOOK_COPIES (book_id, branch_id, no_of_copies) VALUES (?, ?, 5)", (bid, i), commit=True)
            
            self.bid_cb.config(values=self.get_book_ids())
            messagebox.showinfo("Success", f"Book ID {bid} added and seeded to all branches.")

        tk.Button(tab, text="Add Book Globally", command=action, bg="#FF9800", fg="white").pack(pady=20)

    # --- REQ 4 & 5: Reports ---
    def setup_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        # Req 4: Loans per branch (Using branch_name from LIBRARY_BRANCH)
        tk.Label(tab, text="Copies Loaned Out per Branch (By Title)", font=('Arial', 10, 'bold')).pack(pady=5)
        title_ent = tk.Entry(tab); title_ent.pack()
        tree4 = self.create_tree(tab, ("Branch Name", "Checkouts"))
        tree4.pack()
        
        def run_req4():
            q = """SELECT LB.branch_name, COUNT(L.book_id) 
                   FROM BOOK_LOANS L 
                   JOIN LIBRARY_BRANCH LB ON L.branch_id = LB.branch_id
                   JOIN BOOK B ON L.book_id = B.book_id 
                   WHERE B.title = ? GROUP BY LB.branch_name"""
            res = self.run_query(q, (title_ent.get(),))
            for item in tree4.get_children(): tree4.delete(item)
            if res:
                for row in res: tree4.insert("", "end", values=row)

        tk.Button(tab, text="Search Branches", command=run_req4).pack(pady=5)

        # Req 5: Late loans (Using Returned_date from schema)
        tk.Label(tab, text="Late Returns (Due Date Range)", font=('Arial', 10, 'bold')).pack(pady=10)
        range_f = tk.Frame(tab)
        range_f.pack()
        tk.Label(range_f, text="Start:").grid(row=0, column=0); sd = tk.Entry(range_f); sd.grid(row=0, column=1)
        tk.Label(range_f, text="End:").grid(row=1, column=0); ed = tk.Entry(range_f); ed.grid(row=1, column=1)
        
        tree5 = self.create_tree(tab, ("Card No", "Book ID", "Days Late"))
        tree5.pack()

        def run_req5():
            q = """SELECT card_no, book_id, (JULIANDAY(Returned_date) - JULIANDAY(due_date)) 
                   FROM BOOK_LOANS WHERE due_date BETWEEN ? AND ? AND Returned_date > due_date"""
            res = self.run_query(q, (sd.get(), ed.get()))
            for item in tree5.get_children(): tree5.delete(item)
            if res:
                for row in res: tree5.insert("", "end", values=row)

        tk.Button(tab, text="Find Late Loans", command=run_req5).pack(pady=5)

    # --- REQ 6: Finance & Fees (Using your View) ---
    def setup_finance_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Finance")
        
        # 6a: Search borrower by balance (from view)
        tk.Label(tab, text="Borrower Total Late Balance", font=('Arial', 10, 'bold')).pack(pady=5)
        search_a = tk.Entry(tab); search_a.pack()
        tree6a = self.create_tree(tab, ("Name", "Total Balance"))
        tree6a.pack()

        def run_req6a():
            # Summarize balance from the view per borrower
            val = f"%{search_a.get()}%"
            q = """SELECT borrower_name, SUM(LateFeeBalance) 
                   FROM vBookLoanInfo WHERE borrower_name LIKE ? 
                   GROUP BY borrower_name ORDER BY SUM(LateFeeBalance) DESC"""
            res = self.run_query(q, (val,))
            for item in tree6a.get_children(): tree6a.delete(item)
            if res:
                for row in res: tree6a.insert("", "end", values=(row[0], f"${row[1]:.2f}"))

        tk.Button(tab, text="Search Fees", command=run_req6a).pack(pady=5)

        # 6b: Specific Late Fee Info from View
        tk.Label(tab, text="Detailed Late Fee View", font=('Arial', 10, 'bold')).pack(pady=10)
        search_b = tk.Entry(tab); search_b.pack()
        tree6b = self.create_tree(tab, ("Book Title", "Late Days", "Fee Status"))
        tree6b.pack()

        def run_req6b():
            val = f"%{search_b.get()}%"
            # Using your view columns: title, LateDays, LateFeeBalance
            q = """SELECT title, LateDays, 
                   CASE WHEN LateFeeBalance = 0 THEN 'Non-Applicable' 
                   ELSE '$' || printf('%.2f', LateFeeBalance) END 
                   FROM vBookLoanInfo WHERE borrower_name LIKE ? OR title LIKE ?"""
            res = self.run_query(q, (val, val))
            for item in tree6b.get_children(): tree6b.delete(item)
            if res:
                for row in res: tree6b.insert("", "end", values=row)

        tk.Button(tab, text="Search Detailed View", command=run_req6b).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = LMS_App(root)
    root.mainloop()
