# Import order is important to avoid circular imports
from ..extensions import db

# Create base classes
Base = db.Model
BaseModel = db.Model

# Import enums after db is defined
from .enums import PaymentStatus, AuditActionType, CommissionSnapshottingType, ClientEntityType, SettingType, SettingKey

# Import models that don't have foreign key dependencies first
from .api_usage import ApiUsage
from .document import Document
from .notification import NotificationPreference, NotificationType, NotificationEvent
from .report import Report, ReportType, ReportStatus
from .audit import AuditTrail

# For backward compatibility
AuditLog = AuditTrail

# Re-export enums for easier access
__all__ = [
    'Base', 'BaseModel', 'db',
    'PaymentStatus', 'AuditActionType', 'CommissionSnapshottingType', 
    'ClientEntityType', 'SettingType', 'SettingKey',
    'PlanType', 'BillingCycle', 'SubscriptionStatus',
    'WalletProvider', 'WalletProviderCurrency', 'WalletProviderTransaction', 'WalletBalance', 'WalletProviderType',
    # Add other models as needed
]
from .transaction import Transaction
from .platform import Platform, PlatformType, PlatformSetting, PlatformIntegration, PlatformWebhook
from .commission_snapshot import CommissionSnapshot, CommissionSnapshottingType
from .client_setting import ClientSetting, ClientSettingKey
from .currency import Currency, ClientBalance, ClientCommission, CurrencyRate

# Import base models first
from .client import Client, Invoice, ClientDocument, ClientNotificationPreference
from .client_wallet import ClientWallet, ClientPricingPlan

# Then import RecurringPayment before Payment since Payment references it
from .recurring_payment import RecurringPayment

# Then import Withdrawal before Payment since Payment references it
from .withdrawal import Withdrawal, WithdrawalRequest, WithdrawalStatus

# Finally import Payment which has the relationship to RecurringPayment
from .payment import Payment

# Import wallet provider models
from .wallet_provider import WalletProvider, WalletProviderCurrency, WalletProviderTransaction, WalletBalance, WalletProviderType

# Import subscription models
from .pricing_plan import PricingPlan, PlanType, BillingCycle
from .subscription import Subscription, SubscriptionStatus

# Import models with dependencies
from .user import User
from .admin import AdminUser
from .role import Role
from .support_ticket import SupportTicket

# Import package-related models
from .client_package import ClientPackage, Feature, PackageFeature, ClientSubscription, ClientType
from .package_payment import PackageActivationPayment, FlatRateSubscriptionPayment, SubscriptionBillingCycle, SubscriptionStatus
from .setting import Setting

# Import wallet provider models
from .wallet_provider import WalletProvider, WalletProviderCurrency, WalletBalance, WalletProviderTransaction

# Export enums directly
PaymentStatus = PaymentStatus
AuditActionType = AuditActionType
CommissionSnapshottingType = CommissionSnapshottingType
ClientType = ClientType
SettingType = SettingType
SettingKey = SettingKey

# Export models
__all__ = [
    # Base models
    'Base', 'BaseModel',
    
    # Main models
    'User', 'AdminUser', 'Role',
    'Client', 'ClientWallet', 'ClientPricingPlan', 'ClientSetting', 'ClientDocument', 'ClientNotificationPreference', 'Invoice',
    'Platform', 'PlatformType', 'PlatformSetting', 'PlatformIntegration', 'PlatformWebhook',
    'Payment', 'RecurringPayment', 
    'Withdrawal', 'WithdrawalRequest', 'WithdrawalStatus',
    'Document', 
    'NotificationPreference', 'NotificationType', 'NotificationEvent',
    'Report', 'ReportType', 'ReportStatus',
    'AuditTrail', 'AuditLog', 
    'Transaction',
    'ApiUsage', 
    'CommissionSnapshot', 'CommissionSnapshottingType',
    'Setting',
    'Currency', 'ClientBalance', 'ClientCommission', 'CurrencyRate',
    
    # Enums
    'PaymentStatus',
    'AuditActionType',
    'ClientType',
    'SettingType',
    'SettingKey',
    'ClientSettingKey',

    # Support Ticket
    'SupportTicket',

    # Package and Subscription
    'ClientPackage', 'Feature', 'PackageFeature', 'ClientSubscription', 'PackageActivationPayment', 'FlatRateSubscriptionPayment', 'SubscriptionBillingCycle', 'SubscriptionStatus',
    
    # Wallet Provider
    'WalletProvider', 'WalletProviderCurrency', 'WalletBalance', 'WalletProviderTransaction'
]
