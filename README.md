# 📚 Autonomous Rule-Based Library Agent

A fully autonomous, rule-based library management and inventory tracking system built with **Python**, **Streamlit**, **SQLite**, and **Pandas** — running entirely on deterministic logic with **zero external AI APIs**.

---

## ✨ Features

- **📖 Catalog & Inventory Management:** View real-time book availability, status (Available/Borrowed), and due dates stored securely in local database memory.
- **📤 Book Borrowing / Issuance:** Automatically assigns due dates (14-day default cycle) and updates member records.
- **📥 Return & Fine Calculation Engine:** Deterministic rule-based fine calculation (Rs. 50 per late day) with built-in fine payment validation and database logging.
- **📊 Transaction History:** Complete relational logging of all past borrowing and return transactions joined across members and books.
- **🎨 Modern Dual-Theme UI:** Professional clean white main workspace paired with a deep navy blue sidebar navigation and full-width borderless elements.

---

## 🌐 Live Demo
- **Experience the App Live:** [View Streamlit App](https://your-streamlit-app-link.streamlit.app)


## 🛠️ Tech Stack

- **Frontend & UI:** Python Streamlit (Custom CSS injections for advanced styling)
- **Database:** SQLite (`library.db`) with native relational schema (Members, Books, Transactions)
- **Data Processing:** Pandas DataFrames
- **Environment:** Python Virtual Environment (`.venv`)

---

## 🚀 Getting Started Locally

Follow these steps to set up and run the project on your local machine:

### 1. Navigate to Project Directory
```bash
cd Library_Agent

```

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

```

### 3. Install Dependencies

```bash
pip install streamlit pandas

```

### 4. Run the Streamlit Application

```bash
streamlit run app.py

```

---

## 📂 Project Architecture

```text
Library_Agent/
│
├── .venv/                  # Python Virtual Environment
├── library.db              # Local SQLite Database (Auto-initialized)
├── app.py                  # Main Streamlit Application Script
└── README.md               # Project Documentation

```

---

## ⚙️ Database Schema

* **`members`**: Stores library member details (`member_id`, `name`).
* **`books`**: Tracks inventory status (`book_id`, `title`, `status`, `due_date`).
* **`transactions`**: Records checkout history, return dates, fine incurred, and fine paid (`tx_id`, `member_id`, `book_id`, `return_date`, `fine_incurred`, `fine_paid`).

---

## 👤 Author

* **Alina Zahra**
* [GitHub Profile](https://github.com/AlinaZahraHub)
* [LinkedIn Profile](https://www.linkedin.com/in/alina-zahra12/)
