import os
import sqlite3

# Connect to database
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Drop all tables
print("Dropping tables...")
try:
    cursor.execute("DROP TABLE IF EXISTS clients")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS payments")
    cursor.execute("DROP TABLE IF EXISTS withdrawals")
    cursor.execute("DROP TABLE IF EXISTS audit_trail")
    cursor.execute("DROP TABLE IF EXISTS platforms")
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute("DROP TABLE IF EXISTS notification_preferences")
    cursor.execute("DROP TABLE IF EXISTS invoices")
    cursor.execute("DROP TABLE IF EXISTS api_usage")
    cursor.execute("DROP TABLE IF EXISTS report")
    cursor.execute("DROP TABLE IF EXISTS client_documents")
    cursor.execute("DROP TABLE IF EXISTS client_notification_preferences")
except sqlite3.Error as e:
    print(f"Error dropping tables: {e}")

# Create tables with proper schema
print("Creating tables...")
try:
    cursor.execute("""
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company_name VARCHAR(255) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            deposit_commission NUMERIC(5,4) DEFAULT 0.035 NOT NULL,
            withdrawal_commission NUMERIC(5,4) DEFAULT 0.015 NOT NULL,
            deposit_commission_rate FLOAT DEFAULT 0.035 NOT NULL,
            withdrawal_commission_rate FLOAT DEFAULT 0.015 NOT NULL,
            balance NUMERIC(18,8) DEFAULT 0 NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test data
    print("Inserting test data...")
    cursor.execute("""
        INSERT INTO users (email, password_hash, is_admin, is_active)
        VALUES ('admin@paycrypt.online', 'pbkdf2:sha256:260000$Xt4gZ37Z$2d204a5ff67cd19d0e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e', 1, 1)
    """)
    
    cursor.execute("""
        INSERT INTO clients (company_name, email, deposit_commission, withdrawal_commission,
                           deposit_commission_rate, withdrawal_commission_rate, balance, is_active)
        VALUES ('Test Client', 'test@client.com', 0.035, 0.015, 0.035, 0.015, 0, 1)
    """)
    
    conn.commit()
    print("Database fixed successfully!")
except sqlite3.Error as e:
    print(f"Error creating tables: {e}")
finally:
    conn.close()
