
import sqlite3

# ----------------------------------------
# 1. DATABASE CONFIGURATION
# ----------------------------------------


import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE = os.getenv(
    "DATABASE_PATH",
    str(BASE_DIR / "energyops.db")
)



# ----------------------------------------
# 2. CREATE DATABASE AND TABLES
# ----------------------------------------

def create_database():

    # Connect to SQLite database
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # ------------------------------------
    # TABLE 1: INSTALLATIONS
    # ------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS installations (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            installation_date TEXT,
            status TEXT NOT NULL
        )
    """)

    # Fictional customer data for testing
    sample_data = [
        (101, "Anita", "2026-10-20", "Delayed"),
        (102, "Rahul", "2026-10-25", "Scheduled"),
        (103, "Maria", "2026-10-18", "Completed"),
    ]

    # Insert sample customers
    cursor.executemany("""
        INSERT OR IGNORE INTO installations
        (
            customer_id,
            customer_name,
            installation_date,
            status
        )
        VALUES (?, ?, ?, ?)
    """, sample_data)

    # ------------------------------------
    # TABLE 2: SUPPORT TICKETS
    # ------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Save all changes
    connection.commit()

    # Close database connection
    connection.close()

    print("EnergyOps database created successfully!")
    print("Installations table ready.")
    print("Support tickets table ready.")


# ----------------------------------------
# 3. RUN DATABASE SETUP
# ----------------------------------------

if __name__ == "__main__":
    create_database()
