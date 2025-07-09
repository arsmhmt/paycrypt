#!/usr/bin/env python3
"""
Investigate the critical ID overlap security issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models import AdminUser

def investigate_id_overlap():
    """Investigate ID overlap between User and AdminUser tables"""
    app = create_app()
    
    with app.app_context():
        print("=== ID OVERLAP INVESTIGATION ===\n")
        
        # Get all User IDs
        users = User.query.all()
        user_ids = [(u.id, u.username, u.email) for u in users]
        
        # Get all AdminUser IDs
        admins = AdminUser.query.all()
        admin_ids = [(a.id, a.username, a.email) for a in admins]
        
        print("CLIENT USERS:")
        for user_id, username, email in user_ids:
            print(f"  ID: {user_id}, Username: {username}, Email: {email}")
        
        print("\nADMIN USERS:")
        for admin_id, username, email in admin_ids:
            print(f"  ID: {admin_id}, Username: {username}, Email: {email}")
        
        # Check for ID overlaps
        user_id_set = set([u[0] for u in user_ids])
        admin_id_set = set([a[0] for a in admin_ids])
        overlapping_ids = user_id_set.intersection(admin_id_set)
        
        print(f"\n=== ID OVERLAP ANALYSIS ===")
        print(f"User IDs: {sorted(user_id_set)}")
        print(f"Admin IDs: {sorted(admin_id_set)}")
        print(f"Overlapping IDs: {sorted(overlapping_ids)}")
        
        if overlapping_ids:
            print(f"\n🚨 CRITICAL SECURITY ISSUE:")
            print(f"The following IDs exist in BOTH tables: {sorted(overlapping_ids)}")
            
            for overlap_id in overlapping_ids:
                user = User.query.get(overlap_id)
                admin = AdminUser.query.get(overlap_id)
                print(f"\nID {overlap_id}:")
                print(f"  As User: {user.username} ({user.email})")
                print(f"  As Admin: {admin.username} ({admin.email})")
                
                # Test what the user_loader would return
                print(f"  User_loader priority test...")
                print(f"    Step 1: Try User model -> {user}")
                print(f"    Step 2: Try Admin model -> {admin}")
                print(f"    Result: User_loader would return User model first!")
        else:
            print("✅ No ID overlaps found")
        
        print("\n=== SOLUTION RECOMMENDATION ===")
        if overlapping_ids:
            print("IMMEDIATE ACTIONS REQUIRED:")
            print("1. 🔥 This is a critical security vulnerability!")
            print("2. 📋 Client and admin users should have completely separate ID spaces")
            print("3. 🔧 Consider using UUIDs or prefixed IDs to ensure no overlap")
            print("4. 🛡️  Add additional checks in user_loader to prevent cross-authentication")
            print("5. 🧹 Clean up the database to ensure proper separation")

if __name__ == "__main__":
    investigate_id_overlap()
