import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class LMS_App:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Team 8")
        self.root.geometry("1000x850")
        
        # Ensure database is 'LMS.db' as per demo requirements
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
            messagebox.showerror("Database Error", str(e))
            return None

    def create_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=6)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        return tree

    # --- REQ 1: Checkout & Trigger ---
    def setup_checkout_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Checkouts")
        
        tk.Label(tab, text="Book ID:").grid(row=0, column=0, pady=5)
        bid = tk.Entry(tab); bid.grid(row=0, column=1)
        tk.Label(tab, text="Branch ID:").grid(row=1, column=0, pady=5)
        brid = tk.Entry(tab); brid.grid(row=1, column=1)
        tk.Label(tab, text="Card No:").grid(row=2, column=0, pady=5)
        cno = tk.Entry(tab); cno.grid(row=2, column=1)

        tree = self.create_tree(tab, ("Book ID", "Branch ID", "Current Copies"))
        tree.grid(row=4, column=0, columnspan=2, pady=10)

        def action():
            today = datetime.now().strftime('%Y-%m-%d')
            # Trigger handles the copy decrement automatically in the background
            q = "INSERT INTO Book_Loans (Book_Id, Branch_Id, Card_No, Date_Out, Due_Date) VALUES (?, ?, ?, ?, ?)"
            self.run_query(q, (bid.get(), brid.get(), cno.get(), today, '2026-05-30'), commit=True)
            
            res = self.run_query("SELECT Book_Id, Branch_Id, No_Of_Copies FROM Book_Copies WHERE Book_Id=?", (bid.get(),))
            for item in tree.get_children(): tree.delete(item)
            for row in res: tree.insert("", "end", values=row)
            messagebox.showinfo("Success", "Checkout recorded. Trigger updated Book_Copies.")

        tk.Button(tab, text="Submit Checkout", command=action).grid(row=3, column=0, columnspan=2, pady=10)

    # --- REQ 2: New Borrower ---
    def setup_borrower_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Borrowers")
        tk.Label(tab, text="Name:").pack(); name = tk.Entry(tab); name.pack()
        tk.Label(tab, text="Address:").pack(); addr = tk.Entry(tab); addr.pack()
        tk.Label(tab, text="Phone:").pack(); ph = tk.Entry(tab); ph.pack()

        def action():
            q = "INSERT INTO Borrower (Name, Address, Phone) VALUES (?, ?, ?)"
            card_no = self.run_query(q, (name.get(), addr.get(), ph.get()), commit=True)
            messagebox.showinfo("New Library Card", f"Assigned Card Number: {card_no}")

        tk.Button(tab, text="Register", command=action).pack(pady=10)

    # --- REQ 3: Global Book Addition ---
    def setup_book_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add Books")
        tk.Label(tab, text="Title:").pack(); title = tk.Entry(tab); title.pack()
        tk.Label(tab, text="Publisher:").pack(); pub = tk.Entry(tab); pub.pack()
        tk.Label(tab, text="Author:").pack(); auth = tk.Entry(tab); auth.pack()

        def action():
            bid = self.run_query("INSERT INTO Book (Title, Publisher_Name) VALUES (?, ?)", (title.get(), pub.get()), commit=True)
            self.run_query("INSERT INTO Book_Authors (Book_Id, Author_Name) VALUES (?, ?)", (bid, auth.get()), commit=True)
            # Add to all 5 branches with 5 copies [cite: 42]
            for i in range(1, 6):
                self.run_query("INSERT INTO Book_Copies (Book_Id, Branch_Id, No_Of_Copies) VALUES (?, ?, 5)", (bid, i), commit=True)
            messagebox.showinfo("Success", f"Book {bid} seeded to all 5 branches.")

        tk.Button(tab, text="Add to All Branches", command=action).pack(pady=10)

    # --- REQ 4 & 5: Search Reports ---
    def setup_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        # Req 4: Loans per branch [cite: 44]
        tk.Label(tab, text="Req 4: Loaned Copies per Branch", font=('Arial', 10, 'bold')).pack(pady=5)
        title_ent = tk.Entry(tab); title_ent.pack()
        tree4 = self.create_tree(tab, ("Branch Name", "Copies Loaned Out"))
        tree4.pack()
        tk.Button(tab, text="Check Loans", command=lambda: self.run_req4(title_ent, tree4)).pack(pady=5)

        # Req 5: Late loans by date range [cite: 45]
        tk.Label(tab, text="Req 5: Late Loans by Due Date Range", font=('Arial', 10, 'bold')).pack(pady=5)
        range_frame = tk.Frame(tab)
        range_frame.pack()
        tk.Label(range_frame, text="Start (YYYY-MM-DD):").grid(row=0, column=0)
        start_d = tk.Entry(range_frame); start_d.grid(row=0, column=1)
        tk.Label(range_frame, text="End (YYYY-MM-DD):").grid(row=1, column=0)
        end_d = tk.Entry(range_frame); end_d.grid(row=1, column=1)
        
        tree5 = self.create_tree(tab, ("Card No", "Title", "Days Late"))
        tree5.pack()
        tk.Button(tab, text="Find Late Returns", command=lambda: self.run_req5(start_d, end_d, tree5)).pack(pady=5)

    def run_req4(self, ent, tree):
        q = """SELECT lb.Branch_Name, COUNT(bl.Book_Id) FROM Book_Loans bl 
               JOIN Library_Branch lb ON bl.Branch_Id = lb.Branch_Id
               JOIN Book b ON bl.Book_Id = b.Book_Id WHERE b.Title = ? GROUP BY lb.Branch_Name"""
        res = self.run_query(q, (ent.get(),))
        for item in tree.get_children(): tree.delete(item)
        if res:
            for row in res: tree.insert("", "end", values=row)

    def run_req5(self, start, end, tree):
        # Query checks for returned late (Date > Due) within the range [cite: 45, 46]
        q = """SELECT Card_No, Book_Id, (JULIANDAY(Returned_date) - JULIANDAY(Due_Date)) as DaysLate 
               FROM Book_Loans WHERE Due_Date BETWEEN ? AND ? AND Returned_date > Due_Date"""
        res = self.run_query(q, (start.get(), end.get()))
        for item in tree.get_children(): tree.delete(item)
        if res:
            for row in res: tree.insert("", "end", values=row)

    # --- REQ 6: Finance & Fees ---
    def setup_finance_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Finance")
        
        # 6a: Borrower Search [cite: 48, 50]
        tk.Label(tab, text="6a: Borrower Fee Search", font=('Arial', 10, 'bold')).pack()
        search_a = tk.Entry(tab); search_a.pack()
        tree6a = self.create_tree(tab, ("ID", "Name", "Balance"))
        tree6a.pack()
        tk.Button(tab, text="Search Borrowers", command=lambda: self.run_req6a(search_a, tree6a)).pack(pady=5)

        # 6b: Detailed Book/View Search [cite: 53, 56]
        tk.Label(tab, text="6b: View Search (Borrower ID Required)", font=('Arial', 10, 'bold')).pack()
        search_b = tk.Entry(tab); search_b.pack()
        tree6b = self.create_tree(tab, ("Book Title", "Late Fee"))
        tree6b.pack()
        tk.Button(tab, text="Search View", command=lambda: self.run_req6b(search_b, tree6b)).pack(pady=5)

    def run_req6a(self, ent, tree):
        val = f"%{ent.get()}%"
        # Sort by balance if no filter [cite: 51]
        q = """SELECT Card_No, Name, '$' || printf('%.2f', IFNULL(LateFeeBalance, 0)) 
               FROM Borrower WHERE Card_No LIKE ? OR Name LIKE ? ORDER BY LateFeeBalance DESC"""
        res = self.run_query(q, (val, val))
        for item in tree.get_children(): tree.delete(item)
        for row in res: tree.insert("", "end", values=row)

    def run_req6b(self, ent, tree):
        val = f"%{ent.get()}%"
        # Requirement 6b: NULL becomes 'Non-Applicable' [cite: 56]
        q = """SELECT borrower_name, book_title, 
               CASE WHEN LateFeeBalance IS NULL OR LateFeeBalance = 0 THEN 'Non-Applicable' 
               ELSE '$' || printf('%.2f', LateFeeBalance) END as Fee 
               FROM vBookLoanInfo WHERE Card_No LIKE ? OR book_title LIKE ? 
               ORDER BY LateFeeBalance DESC"""
        res = self.run_query(q, (val, val))
        for item in tree.get_children(): tree.delete(item)
        for row in res: tree.insert("", "end", values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = LMS_App(root)
    root.mainloop()