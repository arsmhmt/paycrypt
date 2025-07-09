"""
Test script to verify the Flask application starts up correctly.
"""
import os
import sys
import logging
from app import create_app

def test_app_creation():
    """Test that the Flask application can be created and configured."""
    # Set up test environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['ADMIN_USERNAME'] = 'testadmin'
    os.environ['ADMIN_PASSWORD'] = 'testpass123'
    os.environ['ADMIN_EMAIL'] = 'testadmin@example.com'
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        stream=sys.stdout
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Creating test application...")
        app = create_app()
        
        # Basic app checks
        assert app is not None
        assert app.config['ENV'] == 'testing'
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is True
        
        # Test database connection
        with app.app_context():
            from app.extensions import db
            db.engine.connect()
            logger.info("Successfully connected to the database")
        
        # Test admin user creation
        with app.app_context():
            from app.models.admin import AdminUser
            admin = AdminUser.query.filter_by(username='testadmin').first()
            assert admin is not None
            assert admin.email == 'testadmin@example.com'
            logger.info("Admin user verified")
        
        logger.info("All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    if test_app_creation():
        print("✅ Application test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Application test failed!")
        sys.exit(1)
