import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class LMS_App:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Team 8")
        self.root.geometry("1000x900")
        
        # Ensure this matches your actual database file name
        self.db_name = 'Test.db' 

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
        """Standardized helper to run SQL and return results."""
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
            print(f"SQL Debug Error: {e}")
            messagebox.showerror("Database Error", f"SQL Error: {str(e)}")
            return None

    # --- DROP DOWN DATA FETCHERS ---
    def get_publisher_names(self):
        """Fetches from PUBLISHER table using the publisher_name column."""
        res = self.run_query("SELECT publisher_name FROM PUBLISHER")
        names = [row[0] for row in res] if res else []
        print(f"DEBUG: Publishers loaded: {names}") # Check your console for this!
        return names

    def get_book_ids(self):
        """Fetches from BOOK table using the book_id column."""
        res = self.run_query("SELECT book_id FROM BOOK")
        ids = [row[0] for row in res] if res else []
        return ids

    def create_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        return tree

    # --- REQ 1: Checkout Tab (with Dropdown) ---
    def setup_checkout_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Checkouts")
        
        input_frame = tk.Frame(tab)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Book ID:").grid(row=0, column=0, sticky='e')
        self.bid_cb = ttk.Combobox(input_frame, values=self.get_book_ids())
        self.bid_cb.grid(row=0, column=1, pady=5)
        # Refresh button for Book IDs
        tk.Button(input_frame, text="🔄", command=lambda: self.bid_cb.config(values=self.get_book_ids())).grid(row=0, column=2, padx=5)

        tk.Label(input_frame, text="Branch ID:").grid(row=1, column=0, sticky='e')
        brid = tk.Entry(input_frame); brid.grid(row=1, column=1, pady=5)

        tk.Label(input_frame, text="Card No:").grid(row=2, column=0, sticky='e')
        cno = tk.Entry(input_frame); cno.grid(row=2, column=1, pady=5)

        tree = self.create_tree(tab, ("Book ID", "Branch ID", "Copies Available"))
        tree.pack(pady=10)

        def action():
            book_id = self.bid_cb.get()
            if not book_id:
                messagebox.showwarning("Input Error", "Please select a Book ID.")
                return

            today = datetime.now().strftime('%Y-%m-%d')
            q = "INSERT INTO BOOK_LOANS (book_id, branch_id, card_no, date_out, due_date) VALUES (?, ?, ?, ?, ?)"
            self.run_query(q, (book_id, brid.get(), cno.get(), today, '2026-05-30'), commit=True)
            
            res = self.run_query("SELECT book_id, branch_id, no_of_copies FROM BOOK_COPIES WHERE book_id=?", (book_id,))
            for item in tree.get_children(): tree.delete(item)
            if res:
                for row in res: tree.insert("", "end", values=row)
            messagebox.showinfo("Success", "Checkout recorded.")

        tk.Button(tab, text="Submit Checkout", command=action, bg="#4CAF50", fg="white").pack(pady=10)

    # --- REQ 2: New Borrower ---
    def setup_borrower_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Borrowers")
        
        tk.Label(tab, text="Add New Borrower", font=('Arial', 12, 'bold')).pack(pady=10)
        tk.Label(tab, text="Name:").pack(); name = tk.Entry(tab); name.pack()
        tk.Label(tab, text="Address:").pack(); addr = tk.Entry(tab); addr.pack()
        tk.Label(tab, text="Phone:").pack(); ph = tk.Entry(tab); ph.pack()

        def action():
            q = "INSERT INTO BORROWER (name, address, phone) VALUES (?, ?, ?)"
            card_no = self.run_query(q, (name.get(), addr.get(), ph.get()), commit=True)
            messagebox.showinfo("Success", f"Borrower registered. Card No: {card_no}")

        tk.Button(tab, text="Register", command=action, bg="#2196F3", fg="white").pack(pady=20)

    # --- REQ 3: Global Book Addition (with Publisher Dropdown) ---
    def setup_book_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add Books")
        
        tk.Label(tab, text="Global Book Entry", font=('Arial', 14, 'bold')).pack(pady=15)
        
        tk.Label(tab, text="Title:").pack()
        title = tk.Entry(tab, width=40); title.pack(pady=5)
        
        tk.Label(tab, text="Select Publisher:").pack()
        # Dropdown initialized with data from PUBLISHER table
        self.pub_cb = ttk.Combobox(tab, values=self.get_publisher_names(), width=37)
        self.pub_cb.pack(pady=5)
        
        # Refresh button in case you just imported a CSV
        tk.Button(tab, text="🔄 Refresh Publisher List", 
                  command=lambda: self.pub_cb.config(values=self.get_publisher_names())).pack(pady=5)
        
        tk.Label(tab, text="Author Name:").pack()
        auth = tk.Entry(tab, width=40); auth.pack(pady=5)

        def action():
            t = title.get()
            p = self.pub_cb.get()
            a = auth.get()
            
            if not t or not p:
                messagebox.showwarning("Input Error", "Title and Publisher are required.")
                return
                
            # book_publisher links to publisher_name in your schema
            bid = self.run_query("INSERT INTO BOOK (title, book_publisher) VALUES (?, ?)", (t, p), commit=True)
            self.run_query("INSERT INTO BOOK_AUTHORS (book_id, author_name) VALUES (?, ?)", (bid, a), commit=True)
            
            # Auto-seed to existing branches
            branches = self.run_query("SELECT branch_id FROM LIBRARY_BRANCH")
            if branches:
                for b_id in branches:
                    self.run_query("INSERT INTO BOOK_COPIES (book_id, branch_id, no_of_copies) VALUES (?, ?, 5)", (bid, b_id[0]), commit=True)
            
            # Refresh the checkout dropdown to include the new book
            self.bid_cb.config(values=self.get_book_ids())
            messagebox.showinfo("Success", f"Book added successfully with ID: {bid}")

        tk.Button(tab, text="Add Book Globally", command=action, bg="#FF9800", fg="white", font=('Arial', 11, 'bold')).pack(pady=20)

    # --- REQ 4 & 5: Reports ---
    def setup_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        # Req 4
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

        # Req 5
        tk.Label(tab, text="Late Returns (Due Date Range)", font=('Arial', 10, 'bold')).pack(pady=10)
        range_f = tk.Frame(tab); range_f.pack()
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

    # --- REQ 6: Finance & Fees ---
    def setup_finance_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Finance")
        
        tk.Label(tab, text="Borrower Total Late Balance", font=('Arial', 10, 'bold')).pack(pady=5)
        search_a = tk.Entry(tab); search_a.pack()
        tree6a = self.create_tree(tab, ("Name", "Total Balance"))
        tree6a.pack()

        def run_req6a():
            val = f"%{search_a.get()}%"
            q = """SELECT borrower_name, SUM(LateFeeBalance) 
                   FROM vBookLoanInfo WHERE borrower_name LIKE ? 
                   GROUP BY borrower_name ORDER BY SUM(LateFeeBalance) DESC"""
            res = self.run_query(q, (val,))
            for item in tree6a.get_children(): tree6a.delete(item)
            if res:
                for row in res: tree6a.insert("", "end", values=(row[0], f"${row[1]:.2f}"))
        tk.Button(tab, text="Search Fees", command=run_req6a).pack(pady=5)

        tk.Label(tab, text="Detailed Late Fee View", font=('Arial', 10, 'bold')).pack(pady=10)
        search_b = tk.Entry(tab); search_b.pack()
        tree6b = self.create_tree(tab, ("Book Title", "Late Days", "Fee Status"))
        tree6b.pack()

        def run_req6b():
            val = f"%{search_b.get()}%"
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
