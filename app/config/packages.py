"""
Client Package and Feature Access Configuration

This module defines the central configuration for package-to-feature mappings
and client status synchronization logic.
"""

# Package to Feature Mapping (Single Source of Truth)
PACKAGE_FEATURES = {
    'starter_commission': [
        'api_basic', 
        'history_view'
    ],
    'business_commission': [
        'api_basic', 
        'api_advanced',
        'wallet_management', 
        'history_view'
    ],
    'enterprise_commission': [
        'api_basic', 
        'api_advanced', 
        'dashboard_analytics', 
        'dashboard_realtime',
        'wallet_management', 
        'support_priority', 
        'history_view'
    ],
    'basic_flat_rate': [
        'api_basic', 
        'wallet_management', 
        'history_view'
    ],
    'premium_flat_rate': [
        'api_basic', 
        'api_advanced', 
        'dashboard_analytics', 
        'wallet_management', 
        'support_priority', 
        'history_view'
    ],
    'professional_flat_rate': [
        'api_basic', 
        'api_advanced', 
        'dashboard_analytics', 
        'dashboard_realtime', 
        'wallet_management', 
        'support_priority', 
        'history_view'
    ]
}

# Feature Descriptions for UI Display
FEATURE_DESCRIPTIONS = {
    'api_basic': 'Basic API Access',
    'api_advanced': 'Advanced API Features',
    'dashboard_analytics': 'Analytics Dashboard',
    'dashboard_realtime': 'Real-time Dashboard Updates',
    'wallet_management': 'Wallet Management',
    'support_priority': 'Priority Support',
    'history_view': 'Transaction History Access'
}

# Package Display Names
PACKAGE_DISPLAY_NAMES = {
    'starter_commission': 'Starter Commission',
    'business_commission': 'Business Commission',
    'enterprise_commission': 'Enterprise Commission',
    'basic_flat_rate': 'Basic Flat Rate',
    'premium_flat_rate': 'Premium Flat Rate',
    'professional_flat_rate': 'Professional Flat Rate'
}

def get_client_features(package_slug):
    """
    Get all features available for a specific package.
    
    Args:
        package_slug (str): The package slug (e.g., 'premium', 'basic')
        
    Returns:
        list: List of feature names available for this package
    """
    return PACKAGE_FEATURES.get(package_slug, [])

def client_has_feature(client, feature_name):
    """
    Check if a client has access to a specific feature based on their package.
    
    Args:
        client: Client model instance
        feature_name (str): Name of the feature to check
        
    Returns:
        bool: True if client has access to the feature, False otherwise
    """
    if not client or not client.package:
        return False
    
    package_features = get_client_features(client.package.slug)
    return feature_name in package_features

def get_package_display_name(package_slug):
    """
    Get the display name for a package.
    
    Args:
        package_slug (str): The package slug
        
    Returns:
        str: Display name for the package
    """
    return PACKAGE_DISPLAY_NAMES.get(package_slug, package_slug.title())

def sync_client_status_with_package(client):
    """
    Synchronize client status with their assigned package.
    This ensures status always matches the package for consistency.
    
    Args:
        client: Client model instance
        
    Returns:
        str: The synchronized status
    """
    if not client.package:
        return 'inactive'
    
    # Status = Package slug for consistency
    return client.package.slug

class FeatureAccessMixin:
    """
    Mixin class for Client model to add feature access methods.
    """
    
    def has_feature(self, feature_name):
        """
        Check if this client has access to a specific feature.
        Combines package features with manual overrides.
        """
        # Start with base features from package
        base_features = []
        if self.package:
            base_features = get_client_features(self.package.slug)
        
        # Get manual overrides (if any)
        override_features = getattr(self, 'features_override', None) or []
        
        # Combine package features with overrides
        all_features = set(base_features) | set(override_features)
        
        return feature_name in all_features
    
    def get_features(self):
        """Get all features available to this client (package + overrides)."""
        base_features = []
        if self.package:
            base_features = get_client_features(self.package.slug)
        
        override_features = getattr(self, 'features_override', None) or []
        all_features = set(base_features) | set(override_features)
        
        return sorted(list(all_features))
    
    def get_package_features(self):
        """Get only the features from the package (no overrides)."""
        if not self.package:
            return []
        return get_client_features(self.package.slug)
    
    def get_override_features(self):
        """Get only the manually overridden features."""
        return getattr(self, 'features_override', None) or []
    
    def get_status_display(self):
        """Get the display name for this client's status/package."""
        if not self.package:
            return 'No Package'
        return get_package_display_name(self.package.slug)
    
    def sync_status(self):
        """Synchronize this client's status with their package."""
        new_status = sync_client_status_with_package(self)
        if hasattr(self, 'status') and self.status != new_status:
            self.status = new_status
        return new_status

# Template helper functions for Jinja2
def template_helpers():
    """
    Return a dictionary of helper functions for use in Jinja2 templates.
    """
    return {
        'client_has_feature': client_has_feature,
        'get_client_features': get_client_features,
        'get_package_display_name': get_package_display_name,
        'FEATURE_DESCRIPTIONS': FEATURE_DESCRIPTIONS,
        'PACKAGE_DISPLAY_NAMES': PACKAGE_DISPLAY_NAMES,
        'PACKAGE_FEATURES': PACKAGE_FEATURES
    }
