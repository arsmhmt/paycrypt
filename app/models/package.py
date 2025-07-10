"""Package and Feature models for managing subscription packages and their features."""
from datetime import datetime
from app.extensions import db
from .base import BaseModel

class PackageFeature(BaseModel):
    """Model for storing individual features that can be assigned to packages."""
    __tablename__ = 'package_features'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    display_name = db.Column(db.String(100))
    is_parameterized = db.Column(db.Boolean, default=False, nullable=False)
    default_value = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    package_assignments = db.relationship('PackageFeatureAssignment', back_populates='feature', lazy='dynamic')
    
    def __repr__(self):
        return f'<PackageFeature {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'display_name': self.display_name,
            'is_parameterized': self.is_parameterized,
            'default_value': self.default_value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Package(BaseModel):
    """Model for subscription packages."""
    __tablename__ = 'packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    price_monthly = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    price_yearly = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    features = db.relationship('PackageFeatureAssignment', back_populates='package', lazy='dynamic')
    
    def __repr__(self):
        return f'<Package {self.name}>'
    
    def to_dict(self, include_features=False):
        """Convert model to dictionary for JSON serialization."""
        result = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'price_monthly': float(self.price_monthly) if self.price_monthly else 0,
            'price_yearly': float(self.price_yearly) if self.price_yearly else 0,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_features:
            result['features'] = [
                {
                    'id': fa.feature.id,
                    'name': fa.feature.name,
                    'value': fa.value,
                    'display_name': fa.feature.display_name or fa.feature.name.replace('_', ' ').title()
                }
                for fa in self.features.join(PackageFeature).filter(PackageFeature.is_active == True).all()
            ]
            
        return result


class PackageFeatureAssignment(BaseModel):
    """Association table between Package and PackageFeature with additional data."""
    __tablename__ = 'package_feature_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id', ondelete='CASCADE'), nullable=False, index=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('package_features.id', ondelete='CASCADE'), nullable=False, index=True)
    value = db.Column(db.String(100), nullable=True)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('package_id', 'feature_id', name='_package_feature_uc'),
    )
    
    # Relationships
    package = db.relationship('Package', back_populates='features')
    feature = db.relationship('PackageFeature', back_populates='package_assignments')
    
    def __repr__(self):
        return f'<PackageFeatureAssignment {self.package.name} - {self.feature.name}>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'package_id': self.package_id,
            'feature_id': self.feature_id,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
