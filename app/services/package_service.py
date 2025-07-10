"""
Package Service

Handles package and feature management in the database.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.client_package import ClientPackage, PackageFeature, ClientType, PackageStatus
from app.models.feature import Feature
from app.utils.logger import logger

class PackageService:
    """Service class for managing packages and features."""

    @staticmethod
    def create_package(name, description, client_type, monthly_price=None, commission_rate=None, 
                      is_active=True, is_popular=False, sort_order=0, max_volume_per_month=None,
                      min_margin_percent=1.20, max_transactions_per_month=None, max_api_calls_per_month=1000):
        """
        Create a new package.
        
        Args:
            name (str): Display name of the package
            description (str): Description of the package
            client_type (ClientType): Type of client (COMMISSION or FLAT_RATE)
            monthly_price (Decimal): Monthly price for flat-rate packages
            commission_rate (Decimal): Commission rate for commission-based packages
            is_active (bool): Whether the package is active
            is_popular (bool): Whether to highlight this package
            sort_order (int): Display order
            max_volume_per_month (Decimal): Maximum monthly volume for flat-rate packages
            min_margin_percent (Decimal): Minimum acceptable margin percentage
            max_transactions_per_month (int): Maximum transactions per month
            max_api_calls_per_month (int): Maximum API calls per month
            
        Returns:
            ClientPackage: The created package or None if failed
        """
        from app.extensions import db
        from decimal import Decimal
        from sqlalchemy.exc import IntegrityError
        
        try:
            # Calculate annual price with 10% discount
            annual_price = Decimal(monthly_price) * Decimal('12') * Decimal('0.9') if monthly_price else None
            
            package = ClientPackage(
                name=name,
                description=description,
                client_type=client_type,
                monthly_price=monthly_price,
                annual_price=annual_price,
                commission_rate=commission_rate,
                status=PackageStatus.ACTIVE if is_active else PackageStatus.INACTIVE,
                is_popular=is_popular,
                sort_order=sort_order,
                max_volume_per_month=max_volume_per_month,
                min_margin_percent=min_margin_percent,
                max_transactions_per_month=max_transactions_per_month,
                max_api_calls_per_month=max_api_calls_per_month,
                supports_monthly=True,
                supports_annual=True,
                annual_discount_percent=10.0
            )
            
            return package
            
        except Exception as e:
            logger.error(f"Error creating package {name}: {str(e)}")
            raise

    @staticmethod
    def create_feature(name, feature_key, description, category, is_premium=False):
        """
        Create a new feature that can be assigned to packages.
        
        Args:
            name (str): Display name of the feature
            feature_key (str): Machine-readable key (unique)
            description (str): Description of the feature
            category (str): Category of the feature (e.g., 'dashboard', 'api', 'wallet')
            is_premium (bool): Whether this is a premium feature
            
        Returns:
            Feature: The created feature or None if failed
        """
        from app.extensions import db
        from sqlalchemy.exc import IntegrityError
        
        try:
            feature = Feature(
                name=name,
                feature_key=feature_key,
                description=description,
                category=category,
                is_premium=is_premium
            )
            
            return feature
            
        except Exception as e:
            logger.error(f"Error creating feature {feature_key}: {str(e)}")
            raise

    @staticmethod
    def assign_feature_to_package(package_id, feature_key, is_included=True, limit_value=None):
        """
        Assign a feature to a package.
        
        Args:
            package_id (int): ID of the package
            feature_key (str): Key of the feature to assign
            is_included (bool): Whether the feature is included
            limit_value (int): Optional limit value for the feature
            
        Returns:
            PackageFeature: The assignment or None if failed
        """
        from app.extensions import db
        from sqlalchemy.exc import IntegrityError
        
        with db.session() as session:
            try:
                # Get the feature by key
                feature = session.query(Feature).filter_by(feature_key=feature_key).first()
                if not feature:
                    logger.error(f"Feature not found: {feature_key}")
                    return None
                    
                # Check if assignment already exists
                assignment = session.query(PackageFeature).filter_by(
                    package_id=package_id,
                    feature_id=feature.id
                ).first()
                
                if assignment:
                    # Update existing assignment
                    assignment.is_included = is_included
                    if limit_value is not None:
                        assignment.limit_value = limit_value
                else:
                    # Create new assignment
                    assignment = PackageFeature(
                        package_id=package_id,
                        feature_id=feature.id,
                        is_included=is_included,
                        limit_value=limit_value
                    )
                    session.add(assignment)
                
                return assignment
                
            except Exception as e:
                logger.error(f"Error assigning feature {feature_key} to package {package_id}: {str(e)}")
                session.rollback()
                return None

    @staticmethod
    def remove_feature_from_package(package_id, feature_key):
        """
        Remove a feature assignment from a package.
        
        Args:
            package_id (int): ID of the package
            feature_key (str): Key of the feature to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        from app.extensions import db
        
        with db.session() as session:
            try:
                # Get the feature by key
                feature = session.query(Feature).filter_by(feature_key=feature_key).first()
                if not feature:
                    logger.error(f"Feature not found: {feature_key}")
                    return False
                    
                assignment = session.query(PackageFeature).filter_by(
                    package_id=package_id,
                    feature_id=feature.id
                ).first()
                
                if assignment:
                    session.delete(assignment)
                    return True
                    
                return False
                
            except Exception as e:
                logger.error(f"Error removing feature {feature_key} from package {package_id}: {str(e)}")
                session.rollback()
                return False

    @staticmethod
    def get_package_features(package_id):
        """
        Get all features assigned to a package.
        
        Args:
            package_id (int): ID of the package
            
        Returns:
            list: List of feature assignments with feature details
        """
        from app.extensions import db
        
        with db.session() as session:
            return session.query(PackageFeature, Feature).join(
                Feature, PackageFeature.feature_id == Feature.id
            ).filter(
                PackageFeature.package_id == package_id,
                PackageFeature.is_included == True
            ).all()

    @staticmethod
    def get_package_by_slug(slug):
        """
        Get a package by its slug.
        
        Args:
            slug (str): Package slug
            
        Returns:
            ClientPackage: The package or None if not found
        """
        from app.extensions import db
        
        with db.session() as session:
            return session.query(ClientPackage).filter_by(slug=slug).first()

    @staticmethod
    def get_feature_by_key(feature_key):
        """
        Get a feature by its key.
        
        Args:
            feature_key (str): Feature key
            
        Returns:
            Feature: The feature or None if not found
        """
        from app.extensions import db
        
        with db.session() as session:
            return session.query(Feature).filter_by(feature_key=feature_key).first()

    @staticmethod
    def initialize_default_packages():
        """Initialize default packages and features."""
        from app.scripts.init_packages import init_features, init_packages
        from app.extensions import db
        
        try:
            with db.session() as session:
                # Initialize features
                features_created = init_features(session)
                
                # Initialize packages
                packages_created = init_packages(session)
                
                session.commit()
                logger.info(f"Initialized {features_created} features and {packages_created} packages")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing default packages: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return False
