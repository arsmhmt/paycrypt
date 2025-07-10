"""
Debug script for package service functionality.
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_package_service():
    logger.info("Starting package service debug...")
    
    try:
        logger.info("Importing modules...")
        from app import create_app
        from app.extensions import db
        from app.models.client_package import ClientPackage, ClientType, PackageStatus
        from app.models.feature import Feature, PackageFeature
        from app.services.package_service import PackageService
        
        logger.info("Creating Flask app...")
        app = create_app()
        
        with app.app_context():
            logger.info("App context created")
            
            # Test database connection
            logger.info("Testing database connection...")
            try:
                db.session.execute('SELECT 1')
                logger.info("Database connection successful")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
                return
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Database tables: {tables}")
            
            # Initialize default packages
            logger.info("Initializing default packages...")
            success = PackageService.initialize_default_packages()
            logger.info(f"Package initialization {'succeeded' if success else 'failed'}")
            
            # List all packages
            packages = ClientPackage.query.all()
            logger.info(f"Found {len(packages)} packages")
            
            for pkg in packages:
                logger.info(f"\nPackage: {pkg.name} (ID: {pkg.id})")
                logger.info(f"Type: {pkg.client_type.value}")
                logger.info(f"Status: {pkg.status.value}")
                
                # Get features
                features = PackageService.get_package_features(pkg.id)
                logger.info(f"Features ({len(features)}):")
                for assignment, feature in features:
                    limit_str = f" (limit: {assignment.limit_value}" if assignment.limit_value else ""
                    logger.info(f"  - {feature.name} ({feature.feature_key}){limit_str}")
            
            logger.info("Debug completed successfully")
            
    except Exception as e:
        logger.error(f"Error during debug: {e}", exc_info=True)

if __name__ == "__main__":
    debug_package_service()
