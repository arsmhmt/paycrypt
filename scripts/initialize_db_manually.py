import os
import sys
import decimal
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import text

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create database connection
engine = create_engine('sqlite:///app.db')

# Drop existing tables
print("Dropping tables...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS clients"))
    conn.execute(text("DROP TABLE IF EXISTS users"))

# Create tables with proper schema
print("Creating tables...")
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE
        )
    """))
    
    conn.execute(text("""
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
            is_active BOOLEAN DEFAULT TRUE
        )
    """))

# Insert test data
print("Inserting test data...")
with engine.connect() as conn:
    # Create admin user
    conn.execute(text("""
        INSERT INTO users (email, password_hash, is_admin, is_active)
        VALUES ('admin@paycrypt.online', 'pbkdf2:sha256:260000$Xt4gZ37Z$2d204a5ff67cd19d0e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e', 1, 1)
    """))
    
    # Create test client
    conn.execute(text("""
        INSERT INTO clients (company_name, email, deposit_commission, withdrawal_commission,
                           deposit_commission_rate, withdrawal_commission_rate, balance, is_active)
        VALUES ('Test Client', 'test@client.com', 0.035, 0.015, 0.035, 0.015, 0, 1)
    """))

print("Database initialized successfully!")
