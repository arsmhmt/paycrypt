"""
Client Package and Feature Access Configuration

This module defines the central configuration for package-to-feature mappings
and client status synchronization logic.
"""
from app.config.config import Config

# Package to Feature Mapping (Single Source of Truth)
PACKAGE_FEATURES = {
    # Commission-based packages
    'starter_commission': [
        'api_basic',
        'history_view',
        'max_coins:15',
        'monthly_tx_limit:100',
        'basic_support',
        'email_reports:weekly'
    ],
    'business_commission': [
        'api_basic',
        'api_advanced',
        'wallet_management',
        'history_view',
        'max_coins:20',
        'monthly_tx_limit:500',
        'priority_support',
        'email_reports:daily',
        'api_rate_limit:1000'
    ],
    'enterprise_commission': [
        'api_basic',
        'api_advanced',
        'dashboard_analytics',
        'dashboard_realtime',
        'wallet_management',
        'support_priority',
        'history_view',
        'max_coins:25',
        'monthly_tx_limit:unlimited',
        'dedicated_support',
        'email_reports:realtime',
        'api_rate_limit:5000',
        'custom_integrations',
        'whitelabel'
    ],
    
    # Flat-rate packages
    'starter_flat_rate': [
        'api_basic',
        'wallet_management',
        'history_view',
        'max_coins:15',
        'monthly_tx_limit:100',
        'basic_support',
        'email_reports:weekly'
    ],
    'business_flat_rate': [
        'api_basic',
        'api_advanced',
        'wallet_management',
        'history_view',
        'dashboard_analytics',
        'max_coins:20',
        'monthly_tx_limit:500',
        'priority_support',
        'email_reports:daily',
        'api_rate_limit:1000'
    ],
    'enterprise_flat_rate': [
        'api_basic',
        'api_advanced',
        'wallet_management',
        'history_view',
        'dashboard_analytics',
        'dashboard_realtime',
        'max_coins:25',
        'monthly_tx_limit:unlimited',
        'dedicated_support',
        'email_reports:realtime',
        'api_rate_limit:5000',
        'custom_integrations',
        'whitelabel',
        'multi_user'
    ]
}

# Feature Descriptions for UI Display
FEATURE_DESCRIPTIONS = {
    # API Features
    'api_basic': 'Basic API Access (REST)',
    'api_advanced': 'Advanced API (WebSockets, Webhooks)',
    'api_rate_limit:1000': '1,000 API requests/hour',
    'api_rate_limit:5000': '5,000 API requests/hour',
    
    # Dashboard Features
    'dashboard_analytics': 'Advanced Analytics Dashboard',
    'dashboard_realtime': 'Real-time Dashboard Updates',
    'history_view': 'Transaction History & Export',
    'wallet_management': 'Multi-wallet Management',
    'email_reports:weekly': 'Weekly Email Reports',
    'email_reports:daily': 'Daily Email Reports',
    'email_reports:realtime': 'Real-time Notifications',
    
    # Support Features
    'basic_support': 'Email Support (48h response)',
    'priority_support': 'Priority Support (24h response)',
    'dedicated_support': 'Dedicated Account Manager',
    'support_priority': 'Priority Support',
    
    # Business Features
    'multi_user': 'Multi-user Access',
    'whitelabel': 'White-label Solution',
    'custom_integrations': 'Custom Integrations',
    
    # Limits
    'max_coins:15': 'Up to 15 Cryptocurrencies',
    'max_coins:20': 'Up to 20 Cryptocurrencies',
    'max_coins:25': 'All 25+ Cryptocurrencies',
    'monthly_tx_limit:100': '100 Monthly Transactions',
    'monthly_tx_limit:500': '500 Monthly Transactions',
    'monthly_tx_limit:unlimited': 'Unlimited Transactions'
}

# Package Display Names and Pricing (in USD)
PACKAGE_DISPLAY_NAMES = {
    # Commission-based packages
    'starter_commission': 'Starter (2.9% + $0.30 per tx)',
    'business_commission': 'Business (2.5% + $0.25 per tx)',
    'enterprise_commission': 'Enterprise (Custom Pricing)',
    
    # Flat-rate packages
    'starter_flat_rate': 'Starter Flat Rate ($49/month)',
    'business_flat_rate': 'Business Flat Rate ($199/month)',
    'enterprise_flat_rate': 'Enterprise Flat Rate ($999/month)'
}

# Package slugs by type for upgrade paths
PACKAGE_TIERS = {
    'commission': ['starter_commission', 'business_commission', 'enterprise_commission'],
    'flat_rate': ['starter_flat_rate', 'business_flat_rate', 'enterprise_flat_rate']
}

# Default package limits
DEFAULT_PACKAGE_LIMITS = {
    'max_coins': 15,
    'monthly_tx_limit': 100,
    'api_rate_limit': 100,
    'support_level': 'basic',
    'reporting': 'weekly'
}

def get_package_limits(package_slug):
    """
    Get all limits and features for a specific package.
    
    Args:
        package_slug (str): The package slug
        
    Returns:
        dict: Dictionary of package limits and features
    """
    features = PACKAGE_FEATURES.get(package_slug, [])
    limits = DEFAULT_PACKAGE_LIMITS.copy()
    
    for feature in features:
        if ':' in feature:
            key, value = feature.split(':', 1)
            if key in ['max_coins', 'monthly_tx_limit', 'api_rate_limit']:
                try:
                    limits[key] = int(value) if value != 'unlimited' else float('inf')
                except (ValueError, TypeError):
                    continue
            elif key in ['email_reports']:
                limits['reporting'] = value
            
    return limits

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
        
        Args:
            feature_name (str): The feature name to check
            
        Returns:
            bool: True if the client has access to the feature
        """
        if not hasattr(self, 'package') or not self.package:
            return False
            
        # Check package features
        package_features = get_client_features(self.package.slug)
        
        # Check for direct feature match
        if feature_name in package_features:
            return True
            
        # Check for parameterized features (e.g., 'max_coins:15')
        for feature in package_features:
            if ':' in feature and feature.startswith(feature_name + ':'):
                return True
                
        return False
    
    def get_feature_value(self, feature_name, default=None):
        """
        Get the value of a parameterized feature.
        
        Args:
            feature_name (str): The base feature name
            default: Default value if feature not found
            
        Returns:
            The feature value or default
        """
        if not hasattr(self, 'package') or not self.package:
            return default
            
        package_features = get_client_features(self.package.slug)
        
        for feature in package_features:
            if ':' in feature and feature.startswith(feature_name + ':'):
                try:
                    return feature.split(':', 1)[1]
                except (IndexError, AttributeError):
                    continue
                    
        return default
    
    def get_package_limits(self):
        """
        Get all limits for the client's current package.
        
        Returns:
            dict: Dictionary of package limits
        """
        if not hasattr(self, 'package') or not self.package:
            return DEFAULT_PACKAGE_LIMITS.copy()
            
        return get_package_limits(self.package.slug)
    
    def get_coin_limit(self):
        """
        Get the maximum number of coins allowed for this client's package.
        
        Returns:
            int: Maximum number of coins allowed
        """
        return int(self.get_feature_value('max_coins', 15))
    
    def get_monthly_tx_limit(self):
        """
        Get the monthly transaction limit for this client's package.
        
        Returns:
            int or float: Transaction limit (float('inf') for unlimited)
        """
        limit = self.get_feature_value('monthly_tx_limit', '100')
        return float('inf') if limit == 'unlimited' else int(limit)
    
    def get_api_rate_limit(self):
        """
        Get the API rate limit (requests per hour) for this client's package.
        
        Returns:
            int: Maximum API requests per hour
        """
        return int(self.get_feature_value('api_rate_limit', 100))
    
    def get_features(self):
        """
        Get all features available to this client.
        
        Returns:
            list: List of feature names available to the client
        """
        if not hasattr(self, 'package') or not self.package:
            return []
            
        features = []
        package_features = get_client_features(self.package.slug)
        
        # Convert parameterized features to display names
        for feature in package_features:
            if ':' in feature:
                base_feature = feature.split(':', 1)[0]
                if base_feature in ['max_coins', 'monthly_tx_limit', 'api_rate_limit', 'email_reports']:
                    features.append(feature)
            else:
                features.append(feature)
                
        return features
    
    def get_feature_display_name(self, feature_name):
        """
        Get the display name for a feature.
        
        Args:
            feature_name (str): The feature name to look up
            
        Returns:
            str: Display name for the feature
        """
        return FEATURE_DESCRIPTIONS.get(feature_name, feature_name.replace('_', ' ').title())
    
    def get_package_display_name(self):
        """
        Get the display name for the client's current package.
        
        Returns:
            str: Display name of the package or "No Package"
        """
        if not hasattr(self, 'package') or not self.package:
            return "No Package"
        return get_package_display_name(self.package.slug)
    
    def get_upgrade_options(self):
        """
        Get available upgrade options for this client.
        
        Returns:
            list: List of dicts with package info for available upgrades
        """
        if not hasattr(self, 'package') or not self.package:
            return []
            
        current_pkg = self.package.slug
        upgrades = []
        
        # Determine package type (flat_rate or commission)
        pkg_type = 'flat_rate' if 'flat_rate' in current_pkg else 'commission'
        
        # Get the current tier index
        try:
            current_idx = PACKAGE_TIERS[pkg_type].index(current_pkg)
            
            # Only show higher tiers as upgrade options
            for i in range(current_idx + 1, len(PACKAGE_TIERS[pkg_type])):
                pkg_slug = PACKAGE_TIERS[pkg_type][i]
                upgrades.append({
                    'slug': pkg_slug,
                    'name': get_package_display_name(pkg_slug),
                    'features': [
                        self.get_feature_display_name(f) 
                        for f in get_client_features(pkg_slug)
                        if ':' not in f  # Skip parameterized features
                    ],
                    'is_recommended': i == current_idx + 1  # Next tier is recommended
                })
                
        except (ValueError, KeyError):
            pass
            
        return upgrades
    
    def can_upgrade_package(self):
        """
        Check if the client can upgrade their package.
        
        Returns:
            bool: True if upgrade options are available, False otherwise
        """
        return len(self.get_upgrade_options()) > 0
    
    def sync_status(self):
        """
        Synchronize this client's status with their package.
        Updates package-specific settings and returns the new status.
        
        Returns:
            str: The new status after synchronization
        """
        if not hasattr(self, 'package') or not self.package:
            return None
            
        # Update client status based on package
        new_status = sync_client_status_with_package(self)
        
        # Update any package-specific settings
        limits = self.get_package_limits()
        
        # Update API rate limits if applicable
        if hasattr(self, 'api_settings'):
            self.api_settings.rate_limit = limits.get('api_rate_limit', 100)
            
        # Update notification preferences if applicable
        if hasattr(self, 'notification_preferences'):
            for pref in self.notification_preferences:
                if pref.notification_type == 'email_reports':
                    pref.frequency = limits.get('reporting', 'weekly')
        
        # Update status if it has changed
        if hasattr(self, 'status') and self.status != new_status:
            self.status = new_status
            
        return new_status

def get_upgrade_package_name(current_package_slug):
    """
    Get the next package name for upgrade based on current package.
    
    Args:
        current_package_slug (str): The current package slug
        
    Returns:
        str: Display name of the next package for upgrade
    """
    # Map of package upgrade paths
    upgrade_path = {
        'starter_commission': 'Business Commission',
        'business_commission': 'Enterprise Commission',
        'basic_flat_rate': 'Premium Flat Rate',
        'premium_flat_rate': 'Professional Flat Rate',
        'enterprise_flat_rate': 'Enterprise Flat Rate'  # No upgrade from enterprise
    }
    
    return upgrade_path.get(current_package_slug, 'a higher plan')

# Template helper functions for Jinja2
def get_route_names():
    """Helper function to get all route names in the application context."""
    from flask import current_app
    return list(current_app.view_functions.keys()) if current_app else []

def template_helpers():
    """
    Return a dictionary of helper functions for use in Jinja2 templates.
    """
    return {
        'client_has_feature': client_has_feature,
        'get_package_display_name': get_package_display_name,
        'get_client_features': get_client_features,
        'get_upgrade_package_name': get_upgrade_package_name,
        'get_route_names': get_route_names,
        'FEATURE_DESCRIPTIONS': FEATURE_DESCRIPTIONS,
        'PACKAGE_DISPLAY_NAMES': PACKAGE_DISPLAY_NAMES,
        'PACKAGE_FEATURES': PACKAGE_FEATURES
    }
