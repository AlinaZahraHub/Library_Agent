import sqlite3
from datetime import datetime, timedelta
import difflib

# ---------------------------------------------------------
# 1. DATABASE SETUP & DUMMY DATA INITIALIZATION
# ---------------------------------------------------------
def init_database():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    # Drop old tables to force a fresh reset on every run
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS books")
    cursor.execute("DROP TABLE IF EXISTS members")
    
    # Create Members Table
    cursor.execute("""
        CREATE TABLE members (
            member_id TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    
    # Create Books Table
    cursor.execute("""
        CREATE TABLE books (
            book_id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            due_date TEXT
        )
    """)
    
    # Create Transactions Table (Added member_id for tracking)
    cursor.execute("""
        CREATE TABLE transactions (
            tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT,
            book_id TEXT,
            return_date TEXT,
            fine_incurred REAL,
            fine_paid REAL
        )
    """)
    
    # Insert Sample Members
    sample_members = [
        ('M001', 'Alina Zahra'),
        ('M002', 'Saniah Malik'),
        ('M003', 'Javeria'),
        ('M004', 'Warda')
    ]
    for member in sample_members:
        cursor.execute("INSERT INTO members (member_id, name) VALUES (?, ?)", member)
        
    # Insert Fresh Sample Books for Testing
    sample_books = [
        ('B101', 'Python Programming', 'Borrowed', '2026-10-01'), # Overdue case (Fine will apply)
        ('B102', 'Data Structures', 'Borrowed', '2026-10-15'),    # On-time case (Future due date, No fine)
        ('B103', 'Database Systems', 'Available', None),           # Already available case
        ('B104', 'Advanced Machine Learning', 'Available', None),  # Additional search book
        ('B105', 'Web Development with React', 'Borrowed', '2026-10-20') # Additional search book
    ]
    
    for book in sample_books:
        cursor.execute("""
            INSERT INTO books (book_id, title, status, due_date) 
            VALUES (?, ?, ?, ?)
        """, book)
        
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 2. MEMBER VALIDATION FUNCTION
# ---------------------------------------------------------
def verify_member(member_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, name FROM members WHERE member_id = ?", (member_id,))
    member = cursor.fetchone()
    conn.close()
    return member # Returns (member_id, name) if found, else None

# ---------------------------------------------------------
# 3. LIBRARY BOOK RETURN AGENT (RULE ENGINE WITH MEMBER AUTH)
# ---------------------------------------------------------
def return_book_agent(member_id, book_id, amount_paid=0.0):
    # Verify Member First
    member = verify_member(member_id)
    if not member:
        return f"[Agent]: Error: Member ID '{member_id}' not found in the system. Please check your Member ID."
    
    member_name = member[1]
    
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    # --- Rule 1: Book Existence Validation Rule ---
    cursor.execute("SELECT book_id, title, status, due_date FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        conn.close()
        return f"[Agent]: Error: Book ID '{book_id}' not found in the system."
    
    b_id, title, status, due_date = book
    
    # --- Rule 2: Active Borrow Status Rule ---
    if status == 'Available':
        conn.close()
        return f"[Agent]: Notice: '{title}' ({b_id}) has already been returned to the library."
    
    # --- Rule 3: Due Date & Fine Calculation Rule ---
    today = datetime.now().date()
    due = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    fine_incurred = 0.0
    days_late = 0
    if today > due:
        days_late = (today - due).days
        fine_per_day = 50.0  # Rs. 50 fine per day
        fine_incurred = days_late * fine_per_day
    
    # --- Rule 4: Fine Payment & Verification Rule ---
    if fine_incurred > 0 and amount_paid < fine_incurred:
        conn.close()
        return f"FINE_REQUIRED|{days_late}|{fine_incurred}|'{title}'"
    
    # --- Rule 5: Database Update & Completion Rule ---
    cursor.execute("UPDATE books SET status = 'Available', due_date = NULL WHERE book_id = ?", (book_id,))
    cursor.execute("INSERT INTO transactions (member_id, book_id, return_date, fine_incurred, fine_paid) VALUES (?, ?, ?, ?, ?)", 
                   (member_id, book_id, str(today), fine_incurred, amount_paid))
    conn.commit()
    conn.close()
    
    if fine_incurred > 0:
        return f"[Agent]: Success ({member_name}): Fine of Rs. {amount_paid} received. '{title}' successfully returned! Transaction closed."
    else:
        return f"[Agent]: Success ({member_name}): '{title}' returned on time (No Fine). Transaction completed!"

# ---------------------------------------------------------
# 4. BOOK ISSUANCE (BORROW) RULE ENGINE WITH MEMBER AUTH
# ---------------------------------------------------------
def borrow_book_agent(member_id, book_id):
    # Verify Member First
    member = verify_member(member_id)
    if not member:
        return f"[Agent]: Error: Member ID '{member_id}' not found in the system. Cannot issue book."
    
    member_name = member[1]
    
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT book_id, title, status FROM books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        conn.close()
        return f"[Agent]: Error: Book ID '{book_id}' not found in the system."
    
    b_id, title, status = book
    
    if status == 'Borrowed':
        conn.close()
        return f"[Agent]: Notice: '{title}' ({b_id}) is currently already borrowed by someone else."
    
    # Assign new due date (14 days from today)
    today = datetime.now().date()
    new_due_date = today + timedelta(days=14)
    
    cursor.execute("UPDATE books SET status = 'Borrowed', due_date = ? WHERE book_id = ?", (str(new_due_date), book_id))
    conn.commit()
    conn.close()
    
    return f"[Agent]: Success ({member_name}): '{title}' ({b_id}) has been successfully issued! Due date: {new_due_date}."

# ---------------------------------------------------------
# 5. TRANSACTION HISTORY FUNCTION
# ---------------------------------------------------------
def show_transaction_history():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.tx_id, t.member_id, m.name, t.book_id, b.title, t.return_date, t.fine_paid
        FROM transactions t
        JOIN members m ON t.member_id = m.member_id
        JOIN books b ON t.book_id = b.book_id
    """)
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        print("\n[Agent]: No transaction history found yet.")
        return
        
    print("\n" + "=" * 85)
    print(f"{'Tx ID':<6} | {'Mem ID':<8} | {'Member Name':<15} | {'Book ID':<8} | {'Title':<20} | {'Fine Paid':<10}")
    print("=" * 85)
    for row in records:
        tx_id, m_id, m_name, b_id, title, ret_date, f_paid = row
        print(f"{tx_id:<6} | {m_id:<8} | {m_name:<15} | {b_id:<8} | {title:<20} | Rs. {f_paid:<6}")
    print("=" * 85)

# ---------------------------------------------------------
# 6. VIEW ALL BOOKS (CATALOG) FUNCTION
# ---------------------------------------------------------
def show_all_books():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT book_id, title, status, due_date FROM books")
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        print("\n[Agent]: No books available in inventory.")
        return
        
    print("\n" + "=" * 70)
    print(f"{'Book ID':<8} | {'Title':<30} | {'Status':<12} | {'Due Date':<12}")
    print("=" * 70)
    for row in records:
        b_id, title, status, due_date = row
        due_str = due_date if due_date else "N/A"
        print(f"{b_id:<8} | {title:<30} | {status:<12} | {due_str:<12}")
    print("=" * 70)

# ---------------------------------------------------------
# 7. BOOK INVENTORY SEARCH FUNCTION
# ---------------------------------------------------------
def search_books(keyword):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT book_id, title, status, due_date 
        FROM books 
        WHERE book_id LIKE ? OR title LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print(f"\n[Agent]: No books found matching '{keyword}'.")
        return
        
    print("\n" + "=" * 70)
    print(f"{'Book ID':<8} | {'Title':<30} | {'Status':<12} | {'Due Date':<12}")
    print("=" * 70)
    for row in results:
        b_id, title, status, due_date = row
        due_str = due_date if due_date else "N/A"
        print(f"{b_id:<8} | {title:<30} | {status:<12} | {due_str:<12}")
    print("=" * 70)

# ---------------------------------------------------------
# 8. INTERACTIVE CHAT INTERFACE WITH MEMBER AUTH
# ---------------------------------------------------------
if __name__ == "__main__":
    init_database()
    print("=" * 65)
    print("WELCOME TO THE LIBRARY AGENT (WITH MEMBER AUTHENTICATION)")
    print("Available Test Members: M001 (Alina Zahra), M002 (Saniah Malik), M003 (Javeria)")
    print("Commands:")
    print("  - Type 'books' to view catalog")
    print("  - Type 'search <keyword>' to find books")
    print("  - Type 'borrow <Member ID> <Book ID>' to issue a book (e.g., borrow M001 B103)")
    print("  - Type 'return <Member ID> <Book ID>' to return a book (e.g., return M001 B101)")
    print("  - Type 'history' to view past transactions")
    print("  - Type 'exit' to quit")
    print("=" * 65)
    
    valid_commands = ["history", "exit", "search", "books", "catalog", "borrow", "return"]
    
    while True:
        user_input = input("\nEnter Command: ").strip()
        
        if not user_input:
            print("[Agent]: Please enter a valid command.")
            continue
            
        parts = user_input.split(maxsplit=2)
        command_candidate = parts[0].lower()
        
        # Check for commands or fuzzy matches
        matches = difflib.get_close_matches(command_candidate, valid_commands, n=1, cutoff=0.6)
        
        if matches:
            matched_command = matches[0]
            
            if matched_command == 'exit':
                print("[Agent]: Goodbye! Have a great day.")
                break
                
            elif matched_command in ['books', 'catalog']:
                show_all_books()
                continue
                
            elif matched_command == 'history':
                show_transaction_history()
                continue
                
            elif matched_command == 'search':
                if len(parts) > 1:
                    search_keyword = parts[1].strip()
                    search_books(search_keyword)
                else:
                    print("[Agent]: Please provide a keyword to search (e.g., search python).")
                continue
                
            elif matched_command == 'borrow':
                if len(parts) >= 3:
                    mem_id = parts[1].strip().upper()
                    bk_id = parts[2].strip().upper()
                    print(borrow_book_agent(mem_id, bk_id))
                else:
                    print("[Agent]: Format error! Use: borrow <Member ID> <Book ID> (e.g., borrow M001 B103).")
                continue
                
            elif matched_command == 'return':
                if len(parts) >= 3:
                    mem_id = parts[1].strip().upper()
                    bk_id = parts[2].strip().upper()
                    
                    # Return logic with fine handling
                    response = return_book_agent(mem_id, bk_id, amount_paid=0.0)
                    
                    if response.startswith("FINE_REQUIRED"):
                        _, days_late, fine_incurred, title = response.split("|")
                        print(f"[Agent]: Warning: This book is {days_late} days late. Total fine is Rs. {fine_incurred}.")
                        
                        try:
                            payment_input = float(input("[Agent]: Enter the fine amount you want to pay (Rs.): ").strip())
                        except ValueError:
                            print("[Agent]: Invalid amount entered. Transaction cancelled.")
                            continue
                        
                        if payment_input >= float(fine_incurred):
                            final_response = return_book_agent(mem_id, bk_id, amount_paid=payment_input)
                            print(final_response)
                        else:
                            shortage = float(fine_incurred) - payment_input
                            print(f"[Agent]: Transaction stopped. Insufficient amount. You still owe Rs. {shortage}.")
                    else:
                        print(response)
                else:
                    print("[Agent]: Format error! Use: return <Member ID> <Book ID> (e.g., return M001 B101).")
                continue
        
        print("[Agent]: Unrecognized command. Please use 'borrow', 'return', 'search', 'books', 'history', or 'exit'.")