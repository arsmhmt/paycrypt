import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Client

# Create database connection
engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Drop all tables
    print("Dropping tables...")
    Base.metadata.drop_all(engine)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(engine)
    
    # Create admin user
    print("Creating admin user...")
    admin = Client(
        company_name='Admin Client',
        email='admin@paycrypt.online',
        deposit_commission_rate=0.035,
        withdrawal_commission_rate=0.015,
        deposit_commission=0.035,
        withdrawal_commission=0.015,
        balance=0.0,
        is_active=True
    )
    session.add(admin)
    session.commit()
    
    print("Database initialized successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    session.rollback()
finally:
    session.close()
