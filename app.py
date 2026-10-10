import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# ---------------------------------------------------------
# DATABASE INITIALIZATION (IF NOT EXISTS)
# ---------------------------------------------------------
def init_database():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    # Create Tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            due_date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT,
            book_id TEXT,
            return_date TEXT,
            fine_incurred REAL,
            fine_paid REAL
        )
    """)
    
    # Insert sample members safely without duplicate primary key conflicts
    sample_members = [
        ('M001', 'JOHN'),
        ('M002', 'HANA'),
        ('M003', 'ALEX'),
        ('M004', 'CHARLIE')
    ]
    cursor.executemany("INSERT OR IGNORE INTO members (member_id, name) VALUES (?, ?)", sample_members)
        
    # Check if books exist, if not insert default data
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ('B101', 'Python Programming', 'Borrowed', '2026-10-01'),
            ('B102', 'Data Structures', 'Borrowed', '2026-10-15'),
            ('B103', 'Database Systems', 'Available', None),
            ('B104', 'Advanced Machine Learning', 'Available', None),
            ('B105', 'Web Development with React', 'Borrowed', '2026-10-20')
        ]
        cursor.executemany("INSERT INTO books (book_id, title, status, due_date) VALUES (?, ?, ?, ?)", sample_books)
        
    conn.commit()
    conn.close()

init_database()

# ---------------------------------------------------------
# STREAMLIT UI CONFIGURATION & NAVY BLUE SIDEBAR STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="Autonomous Rule-Based Library Agent", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    /* Main Content Area - Clean Professional White */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Sidebar Navigation Container - Deep Navy Blue Theme */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        display: none;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 8px;
        background-color: transparent;
        padding: 0px;
        width: 100% !important;
        border: none;
    }
    
    /* Clean Text List Style - No Box / No Border */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: transparent !important;
        border-radius: 6px;
        padding: 10px 12px;
        color: #94a3b8 !important;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none !important;
        box-shadow: none !important;
        width: 100% !important;
        display: flex !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
    }
    
    /* Active / Selected Text Highlight */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background-color: rgba(59, 130, 246, 0.15) !important;
        color: #38bdf8 !important;
        font-weight: 600;
        border: none !important;
        box-shadow: none !important;
    }

    /* Action Buttons Inside Content Area */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7, #0369a1);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369a1, #075985);
        box-shadow: 0 6px 16px rgba(3, 105, 161, 0.4);
        color: white;
    }

    /* Headers styling */
    h1, h2, h3 {
        color: #0f172a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Clean Professional Table Styling */
    [data-testid="stDataFrame"] {
        background-color: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📚 Autonomous Rule-Based Library Agent")
st.markdown("### Powered by Pure Python & SQLite (Zero External AI APIs)")
st.markdown("---")

# Sidebar Navigation Header & Radio Selection
st.sidebar.markdown("<div style='padding: 10px 0;'><span style='color: #38bdf8; font-size: 16px; font-weight: bold; letter-spacing: 1px;'>📌 NAVIGATION PANEL</span></div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

option = st.sidebar.radio(
    "Navigation",
    ["📖 View Catalog & Inventory", "📤 Borrow Book", "📥 Return Book", "📊 Transaction History"],
    label_visibility="collapsed"
)

# ---------------------------------------------------------
# 1. VIEW CATALOG
# ---------------------------------------------------------
if option == "📖 View Catalog & Inventory":
    st.subheader("📖 Library Book Catalog")
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title, status, due_date FROM books")
    books = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(books, columns=["Book ID", "Title", "Status", "Due Date"])
    df["Due Date"] = df["Due Date"].fillna("N/A")
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# 2. BORROW BOOK
# ---------------------------------------------------------
elif option == "📤 Borrow Book":
    st.subheader("📤 Issue / Borrow a Book")
    
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, name FROM members")
    members = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.execute("SELECT book_id, title FROM books WHERE status = 'Available'")
    available_books = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    selected_member = st.selectbox("Select Member", options=list(members.keys()), format_func=lambda x: f"{x} - {members[x]}")
    selected_book = st.selectbox("Select Available Book", options=list(available_books.keys()), format_func=lambda x: f"{x} - {available_books[x]}") if available_books else None
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Confirm & Issue Book"):
        if not selected_book:
            st.error("No books available for borrowing.")
        else:
            conn = sqlite3.connect("library.db")
            cursor = conn.cursor()
            today = datetime.now().date()
            new_due_date = today + timedelta(days=14)
            cursor.execute("UPDATE books SET status = 'Borrowed', due_date = ? WHERE book_id = ?", (str(new_due_date), selected_book))
            conn.commit()
            conn.close()
            st.success(f"Success! Book '{available_books[selected_book]}' issued to {members[selected_member]}. Due Date: {new_due_date}")

# ---------------------------------------------------------
# 3. RETURN BOOK
# ---------------------------------------------------------
elif option == "📥 Return Book":
    st.subheader("📥 Return a Book")
    
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, name FROM members")
    members = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.execute("SELECT book_id, title FROM books WHERE status = 'Borrowed'")
    borrowed_books = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    selected_member = st.selectbox("Select Member", options=list(members.keys()), format_func=lambda x: f"{x} - {members[x]}")
    selected_book = st.selectbox("Select Borrowed Book to Return", options=list(borrowed_books.keys()), format_func=lambda x: f"{x} - {borrowed_books[x]}") if borrowed_books else None
    
    if selected_book:
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT due_date, title FROM books WHERE book_id = ?", (selected_book,))
        due_date_str, title = cursor.fetchone()
        conn.close()
        
        today = datetime.now().date()
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        
        fine_incurred = 0.0
        days_late = 0
        if today > due:
            days_late = (today - due).days
            fine_incurred = days_late * 50.0
            
        st.markdown("<br>", unsafe_allow_html=True)
        if fine_incurred > 0:
            st.warning(f"⚠️ This book is {days_late} days late! Total Fine: Rs. {fine_incurred}")
            payment_input = st.number_input("Enter Fine Amount Paid (Rs.)", min_value=0.0, max_value=float(fine_incurred), step=50.0)
            
            if st.button("Confirm Return & Pay Fine"):
                if payment_input >= fine_incurred:
                    conn = sqlite3.connect("library.db")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET status = 'Available', due_date = NULL WHERE book_id = ?", (selected_book,))
                    cursor.execute("INSERT INTO transactions (member_id, book_id, return_date, fine_incurred, fine_paid) VALUES (?, ?, ?, ?, ?)", 
                                   (selected_member, selected_book, str(today), fine_incurred, payment_input))
                    conn.commit()
                    conn.close()
                    st.success(f"Success! Fine of Rs. {payment_input} received. '{title}' returned successfully.")
                else:
                    st.error(f"Insufficient payment. You still owe Rs. {fine_incurred - payment_input}.")
        else:
            st.info("✅ This book is on time. No fine required.")
            if st.button("Confirm Return"):
                conn = sqlite3.connect("library.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE books SET status = 'Available', due_date = NULL WHERE book_id = ?", (selected_book,))
                cursor.execute("INSERT INTO transactions (member_id, book_id, return_date, fine_incurred, fine_paid) VALUES (?, ?, ?, ?, ?)", 
                               (selected_member, selected_book, str(today), 0.0, 0.0))
                conn.commit()
                conn.close()
                st.success(f"Success! '{title}' returned on time.")

# ---------------------------------------------------------
# 4. TRANSACTION HISTORY
# ---------------------------------------------------------
elif option == "📊 Transaction History":
    st.subheader("📊 Past Transaction History (Database Memory)")
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
    
    if records:
        df_tx = pd.DataFrame(records, columns=["Tx ID", "Member ID", "Member Name", "Book ID", "Title", "Return Date", "Fine Paid"])
        st.dataframe(df_tx, use_container_width=True)
    else:
        st.info("No transactions recorded yet.")
