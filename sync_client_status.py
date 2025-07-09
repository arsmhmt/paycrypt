#!/usr/bin/env python3
"""
Client Status Synchronization Script

This script ensures that all clients have their status field synchronized
with their assigned package slug. This maintains consistency between the
client status and their package capabilities.

Usage:
    python sync_client_status.py
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def sync_client_status():
    """Sync all client status fields with their package slugs"""
    print("🔄 Starting Client Status Synchronization...")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.models.client import Client
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            # Get all clients
            clients = Client.query.all()
            total_clients = len(clients)
            
            print(f"📊 Found {total_clients} clients to check")
            print("-" * 60)
            
            updated_count = 0
            error_count = 0
            
            for client in clients:
                try:
                    old_status = getattr(client, 'status', None)
                    expected_status = None
                    
                    if client.package and hasattr(client.package, 'slug'):
                        expected_status = client.package.slug
                    elif client.package and hasattr(client.package, 'name'):
                        # Fallback: create slug from name
                        expected_status = client.package.name.lower().replace(' ', '_')
                    else:
                        expected_status = 'inactive'
                    
                    # Check if we need to update
                    if not hasattr(client, 'status'):
                        # Add status field if it doesn't exist
                        client.status = expected_status
                        updated_count += 1
                        print(f"✅ {client.company_name} (ID: {client.id}): Added status '{expected_status}'")
                    elif old_status != expected_status:
                        # Update existing status
                        client.status = expected_status
                        updated_count += 1
                        print(f"🔄 {client.company_name} (ID: {client.id}): '{old_status}' → '{expected_status}'")
                    else:
                        print(f"✓ {client.company_name} (ID: {client.id}): Already synced ('{old_status}')")
                        
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error with {client.company_name} (ID: {client.id}): {str(e)}")
            
            # Commit all changes
            if updated_count > 0:
                db.session.commit()
                print("-" * 60)
                print(f"💾 Committed {updated_count} updates to database")
            
            # Summary
            print("=" * 60)
            print("📈 SYNCHRONIZATION SUMMARY")
            print("=" * 60)
            print(f"Total Clients: {total_clients}")
            print(f"✅ Updated: {updated_count}")
            print(f"✓ Already Synced: {total_clients - updated_count - error_count}")
            print(f"❌ Errors: {error_count}")
            
            if updated_count > 0:
                print(f"\n🎉 Successfully synchronized {updated_count} client(s)!")
            else:
                print(f"\n✨ All clients were already synchronized!")
                
            return True
            
    except Exception as e:
        print(f"💥 Fatal error during synchronization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_sync():
    """Verify that all clients are properly synchronized"""
    print("\n🔍 Verifying synchronization...")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.models.client import Client
        
        app = create_app()
        
        with app.app_context():
            clients = Client.query.all()
            issues = []
            
            for client in clients:
                if not hasattr(client, 'status'):
                    issues.append(f"❌ {client.company_name}: Missing status field")
                elif client.package:
                    expected_status = getattr(client.package, 'slug', client.package.name.lower().replace(' ', '_'))
                    if client.status != expected_status:
                        issues.append(f"⚠️ {client.company_name}: Status '{client.status}' doesn't match package '{expected_status}'")
                
            if issues:
                print("🚨 Found synchronization issues:")
                for issue in issues:
                    print(f"  {issue}")
                return False
            else:
                print("✅ All clients are properly synchronized!")
                return True
                
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        return False

def show_client_status_report():
    """Show a detailed report of all client statuses"""
    print("\n📊 CLIENT STATUS REPORT")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.models.client import Client
        
        app = create_app()
        
        with app.app_context():
            clients = Client.query.all()
            
            # Group by status
            status_groups = {}
            for client in clients:
                status = getattr(client, 'status', 'unknown')
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(client)
            
            for status, client_list in sorted(status_groups.items()):
                print(f"\n📦 {status.upper()} ({len(client_list)} clients):")
                for client in client_list[:5]:  # Show first 5
                    package_name = client.package.name if client.package else "No Package"
                    print(f"  • {client.company_name} - {package_name}")
                if len(client_list) > 5:
                    print(f"  ... and {len(client_list) - 5} more")
                    
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")

def main():
    """Main function"""
    print("🚀 Client Status Synchronization Tool")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run synchronization
    success = sync_client_status()
    
    if success:
        # Verify the sync worked
        verify_sync()
        
        # Show status report
        show_client_status_report()
        
        print(f"\n🏁 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    else:
        print("\n💥 Synchronization failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
