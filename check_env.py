import sys
import os

print("=== Python Environment Check ===\n")

# Print Python version
print(f"Python Version: {sys.version}\n")

# Print current working directory
print(f"Current Working Directory: {os.getcwd()}\n")

# List files in current directory
print("Files in current directory:")
for f in os.listdir('.'):
    print(f"  - {f}")
print()

# Try to import Flask
print("Checking Flask installation...")
try:
    import flask
    print(f"  Flask version: {flask.__version__}")
except ImportError:
    print("  Flask is not installed")

# Try to import SQLAlchemy
print("\nChecking SQLAlchemy installation...")
try:
    import sqlalchemy
    print(f"  SQLAlchemy version: {sqlalchemy.__version__}")
except ImportError:
    print("  SQLAlchemy is not installed")

# Try to connect to the database
print("\nChecking database connection...")
try:
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.extensions import db
        db.engine.connect()
        print("  Successfully connected to the database")
except Exception as e:
    print(f"  Error connecting to database: {str(e)}")

print("\nEnvironment check completed")
