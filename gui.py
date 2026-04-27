import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class LMS_App:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Team 8")
        self.root.geometry("1100x800")
        self.db_name = 'Test.db' 

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # References for dropdowns
        self.checkout_bid_cb = None
        self.report_bid_cb = None
        self.pub_cb = None

        self.setup_checkout_tab()  
        self.setup_borrower_tab()  
        self.setup_book_tab()      
        self.setup_reports_tab()   
        self.setup_finance_tab()   

        self.refresh_all_dropdowns()

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
            print(f"SQL ERROR: {e}")
            return None

    def refresh_all_dropdowns(self):
        bids = [r[0] for r in self.run_query("SELECT book_id FROM BOOK")]
        pubs = [r[0] for r in self.run_query("SELECT publisher_name FROM PUBLISHER")]
        if self.checkout_bid_cb: self.checkout_bid_cb.config(values=bids)
        if self.report_bid_cb: self.report_bid_cb.config(values=bids)
        if self.pub_cb: self.pub_cb.config(values=pubs)

    def create_tree(self, parent, cols):
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=8)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150, anchor="center")
        return tree

    # --- TABS ---

    def setup_checkout_tab(self):
        tab = ttk.Frame(self.notebook); self.notebook.add(tab, text="Checkouts")
        center = tk.Frame(tab); center.pack(pady=50)
        
        tk.Label(center, text="Book ID:").grid(row=0, column=0)
        self.checkout_bid_cb = ttk.Combobox(center, state="readonly")
        self.checkout_bid_cb.grid(row=0, column=1)
        
        tk.Label(center, text="Branch ID:").grid(row=1, column=0)
        brid = tk.Entry(center); brid.grid(row=1, column=1)
        
        tk.Label(center, text="Card No:").grid(row=2, column=0)
        cno = tk.Entry(center); cno.grid(row=2, column=1)
        
        tree = self.create_tree(tab, ("Book ID", "Branch ID", "Copies Status"))
        tree.pack(pady=20)

        def action():
            bid = self.checkout_bid_cb.get()
            if not bid: return
            self.run_query("INSERT INTO BOOK_LOANS (book_id, branch_id, card_no, date_out, due_date) VALUES (?, ?, ?, ?, ?)", 
                           (bid, brid.get(), cno.get(), datetime.now().strftime('%Y-%m-%d'), '2026-05-30'), commit=True)
            res = self.run_query("SELECT book_id, branch_id, no_of_copies FROM BOOK_COPIES WHERE book_id=?", (bid,))
            for i in tree.get_children(): tree.delete(i)
            for r in res: tree.insert("", "end", values=r)
            messagebox.showinfo("Success", "Checkout recorded.")

        tk.Button(center, text="Record Checkout", command=action).grid(row=3, columnspan=2, pady=10)

    def setup_borrower_tab(self):
        tab = ttk.Frame(self.notebook); self.notebook.add(tab, text="Borrowers")
        center = tk.Frame(tab); center.pack(pady=100)
        
        tk.Label(center, text="Full Name:").pack(); n = tk.Entry(center); n.pack(pady=5)
        tk.Label(center, text="Address:").pack(); a = tk.Entry(center); a.pack(pady=5)
        tk.Label(center, text="Phone:").pack(); p = tk.Entry(center); p.pack(pady=5)
        
        def action():
            cid = self.run_query("INSERT INTO BORROWER (name, address, phone) VALUES (?, ?, ?)", (n.get(), a.get(), p.get()), commit=True)
            messagebox.showinfo("Success", f"New Card: {cid}")
            
        tk.Button(center, text="Add Borrower", command=action).pack(pady=20)

    def setup_book_tab(self):
        tab = ttk.Frame(self.notebook); self.notebook.add(tab, text="Add Books")
        center = tk.Frame(tab); center.pack(pady=50)
        
        tk.Label(center, text="Book Title:").pack(); t = tk.Entry(center, width=40); t.pack(pady=5)
        
        tk.Label(center, text="Publisher:").pack()
        p_frame = tk.Frame(center)
        p_frame.pack(pady=5)
        self.pub_cb = ttk.Combobox(p_frame, state="readonly", width=25)
        self.pub_cb.pack(side="left", padx=5)
        tk.Button(p_frame, text="Add New", command=self.popup_add_publisher).pack(side="left")
        
        tk.Label(center, text="Author:").pack(); auth = tk.Entry(center, width=40); auth.pack(pady=5)

        def action():
            bid = self.run_query("INSERT INTO BOOK (title, book_publisher) VALUES (?, ?)", (t.get(), self.pub_cb.get()), commit=True)
            self.run_query("INSERT INTO BOOK_AUTHORS (book_id, author_name) VALUES (?, ?)", (bid, auth.get()), commit=True)
            branches = self.run_query("SELECT branch_id FROM LIBRARY_BRANCH")
            for b in branches:
                self.run_query("INSERT INTO BOOK_COPIES (book_id, branch_id, no_of_copies) VALUES (?, ?, 5)", (bid, b[0]), commit=True)
            self.refresh_all_dropdowns()
            messagebox.showinfo("Success", f"Book {bid} added.")

        tk.Button(center, text="Save Book Globally", command=action).pack(pady=20)

    def popup_add_publisher(self):
        pop = tk.Toplevel(self.root); pop.title("New Publisher"); pop.geometry("300x200")
        tk.Label(pop, text="Name:").pack(); p_n = tk.Entry(pop); p_n.pack()
        tk.Label(pop, text="Phone:").pack(); p_p = tk.Entry(pop); p_p.pack()
        tk.Label(pop, text="Address:").pack(); p_a = tk.Entry(pop); p_a.pack()
        def save():
            self.run_query("INSERT INTO PUBLISHER (publisher_name, phone, address) VALUES (?, ?, ?)", (p_n.get(), p_p.get(), p_a.get()), commit=True)
            self.refresh_all_dropdowns(); pop.destroy()
        tk.Button(pop, text="Save", command=save).pack(pady=10)
        
    def setup_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        # --- REQUIREMENT 4: COPIES LOANED BY TITLE ---
        tk.Label(tab, text="Copies Loaned Out per Branch", font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        
        req4_frame = tk.Frame(tab)
        req4_frame.pack(pady=10)
        
        tk.Label(req4_frame, text="Enter Book Title:").grid(row=0, column=0, padx=5)
        title_ent = tk.Entry(req4_frame, width=30)
        title_ent.grid(row=0, column=1, padx=5)
        
        tree4 = self.create_tree(tab, ("Title", "Branch", "Loans"))
        tree4.pack(pady=10)

        def run_req4():
            search = f"%{title_ent.get()}%"
            q = """SELECT B.title, LB.branch_name, COUNT(L.book_id) 
                   FROM BOOK B
                   LEFT JOIN BOOK_LOANS L ON B.book_id = L.book_id
                   LEFT JOIN LIBRARY_BRANCH LB ON L.branch_id = LB.branch_id
                   WHERE B.title LIKE ? GROUP BY LB.branch_name"""
            res = self.run_query(q, (search,))
            for i in tree4.get_children(): tree4.delete(i)
            if res:
                for r in res:
                    branch = r[1] if r[1] else "No Active Loans"
                    count = r[2] if r[1] else 0
                    tree4.insert("", "end", values=(r[0], branch, count))

        tk.Button(req4_frame, text="Search Title", command=run_req4).grid(row=0, column=2, padx=5)

        # --- REQUIREMENT 5: LATE RETURNS ---
        # Separator line
        ttk.Separator(tab, orient='horizontal').pack(fill='x', pady=20)
        
        tk.Label(tab, text="Late Returns Search", font=('Arial', 12, 'bold')).pack(pady=10)
        
        req5_frame = tk.Frame(tab)
        req5_frame.pack(pady=10)
        
        tk.Label(req5_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        sd = tk.Entry(req5_frame, width=15)
        sd.grid(row=0, column=1, padx=5)
        
        tk.Label(req5_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        ed = tk.Entry(req5_frame, width=15)
        ed.grid(row=0, column=3, padx=5)
        
        tree5 = self.create_tree(tab, ("Card No", "Book ID", "Days Late"))
        tree5.pack(pady=10)

        def run_req5():
            # Uses JULIANDAY to calculate the difference between return and due date
            q = """SELECT card_no, book_id, 
                   CAST(JULIANDAY(Returned_date) - JULIANDAY(due_date) AS INTEGER) 
                   FROM BOOK_LOANS 
                   WHERE due_date BETWEEN ? AND ? 
                   AND Returned_date > due_date"""
            res = self.run_query(q, (sd.get(), ed.get()))
            for i in tree5.get_children(): tree5.delete(i)
            if res:
                for r in res: tree5.insert("", "end", values=r)
            else:
                messagebox.showinfo("Report", "No late returns found in this range.")

        tk.Button(req5_frame, text="Find Late Loans", command=run_req5).grid(row=0, column=4, padx=10)
        
    def setup_finance_tab(self):
        tab = ttk.Frame(self.notebook); self.notebook.add(tab, text="Finance")
        center = tk.Frame(tab); center.pack(pady=20)
        
        tk.Label(center, text="Search Borrower (ID or Name):").pack(side="left")
        sa = tk.Entry(center); sa.pack(side="left", padx=10)
        
        # Meaningful columns as per requirement
        tree6a = self.create_tree(tab, ("Borrower ID", "Name", "Total Balance"))
        tree6a.pack(pady=20)
        
        def run_6a():
            val = sa.get().strip()
            search = f"%{val}%"
            
            # The query handles NULLs, Currency formatting, and Sorting
            q = """SELECT card_no, borrower_name, 
                   '$' || printf('%.2f', SUM(IFNULL(LateFeeBalance, 0))) 
                   FROM vBookLoanInfo 
                   WHERE (card_no LIKE ? OR borrower_name LIKE ?) 
                   GROUP BY card_no, borrower_name 
                   ORDER BY 
                   CASE WHEN ? = '' THEN SUM(IFNULL(LateFeeBalance, 0)) ELSE 0 END DESC"""
            
            # Pass the search term 3 times (for ID, Name, and the Order By check)
            res = self.run_query(q, (search, search, val))
            
            for i in tree6a.get_children(): tree6a.delete(i)
            if res:
                for r in res: tree6a.insert("", "end", values=r)

        tk.Button(center, text="Search Fees", command=run_6a).pack(side="left")
        
        tk.Label(tab, text="Detailed Late Fee View", font=('Arial', 10, 'bold')).pack(pady=10)
        sb = tk.Entry(tab); sb.pack()
        tree6b = self.create_tree(tab, ("Book Title", "Days Late", "Fee Amount"))
        tree6b.pack(pady=10)

        def run_6b():
            val = sb.get().strip()
            search = f"%{val}%"
            
            q = """SELECT title, LateDays, 
                   CASE WHEN LateFeeBalance <= 0 THEN '$0.00' 
                   ELSE '$' || printf('%.2f', LateFeeBalance) END 
                   FROM vBookLoanInfo 
                   WHERE (card_no LIKE ? OR borrower_name LIKE ?)
                   ORDER BY LateDays DESC"""
            
            res = self.run_query(q, (search, search))
            
            for i in tree6b.get_children(): tree6b.delete(i)
            if res:
                for r in res: tree6b.insert("", "end", values=r)

        tk.Button(tab, text="Get Detailed Report", command=run_6b).pack(pady=5)
        
if __name__ == "__main__":
    root = tk.Tk(); app = LMS_App(root); root.mainloop()
