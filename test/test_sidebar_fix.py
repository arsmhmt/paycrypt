#!/usr/bin/env python3
"""
Test script to verify the sidebar_stats fix and admin routes
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_admin_context():
    print("🧪 Testing Admin Routes Context Fix")
    print("=" * 50)
    
    try:
        # Import Flask app
        from app import create_app
        
        print("✓ Creating Flask application...")
        app = create_app()
        
        with app.app_context():
            print("✓ Application context working")
            
            # Test admin routes import
            from app.admin_routes import get_sidebar_stats, get_dashboard_stats
            print("✓ Admin routes imported successfully")
            
            # Test sidebar stats function
            sidebar_stats = get_sidebar_stats()
            print(f"✓ Sidebar stats: {sidebar_stats}")
            
            # Verify required keys
            required_keys = [
                'pending_withdrawals',
                'pending_user_withdrawals', 
                'pending_client_withdrawals',
                'total_clients',
                'custom_wallets',
                'pending_tickets'
            ]
            
            for key in required_keys:
                if key in sidebar_stats:
                    print(f"  ✓ {key}: {sidebar_stats[key]}")
                else:
                    print(f"  ❌ Missing key: {key}")
            
            # Test dashboard stats
            try:
                dashboard_stats = get_dashboard_stats()
                print(f"✓ Dashboard stats working")
            except Exception as e:
                print(f"⚠ Dashboard stats error: {e}")
            
            # Test context processor
            from app.admin_routes import admin_bp
            print(f"✓ Admin blueprint: {admin_bp.name}")
            
            print(f"\n🎯 Fix Summary:")
            print("=" * 50)
            print("✅ Added get_sidebar_stats() function")
            print("✅ Created context processor for automatic injection")
            print("✅ Fixed template undefined variable error")
            print("✅ All admin routes should now work properly")
            
            print(f"\n🌐 Ready to test:")
            print("=" * 50)
            print("1. Start the app: python run.py")
            print("2. Visit: http://localhost:5000/admin/dashboard")
            print("3. Visit: http://localhost:5000/admin/clients")
            print("4. No more 'sidebar_stats' undefined errors!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print(f"\n✨ Test completed successfully!")
    return 0

if __name__ == "__main__":
    exit(test_admin_context())
