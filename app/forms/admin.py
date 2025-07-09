from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DecimalField, BooleanField, PasswordField, EmailField, IntegerField, HiddenField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Email, EqualTo, ValidationError, InputRequired
from decimal import Decimal
from ..models import Client, AdminUser, PaymentStatus
from ..models.withdrawal import WithdrawalStatus

class LoginForm(FlaskForm):
    """Form for admin login"""
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=128)])
    remember_me = BooleanField('Remember Me', default=False)
    submit = SubmitField('Login')


class PaymentFilterForm(FlaskForm):
    """Form for filtering payments"""
    status = SelectField(
        'Status',
        choices=[
            ('all', 'All Statuses'),
            (PaymentStatus.PENDING.value, 'Pending'),
            (PaymentStatus.APPROVED.value, 'Approved'),
            (PaymentStatus.REJECTED.value, 'Rejected'),
            (PaymentStatus.FAILED.value, 'Failed'),
            (PaymentStatus.CANCELLED.value, 'Cancelled')
        ],
        default='all',
        validators=[DataRequired()]
    )
    client_id = StringField('Client ID', validators=[Optional()])
    currency = StringField('Currency', validators=[Optional()])
    date_from = StringField('From', validators=[Optional()], render_kw={"type": "date"})
    date_to = StringField('To', validators=[Optional()], render_kw={"type": "date"})
    search = StringField('Search', validators=[Optional()])
    start_date = StringField('Start Date', validators=[Optional()], render_kw={"type": "date"})
    end_date = StringField('End Date', validators=[Optional()], render_kw={"type": "date"})
    submit = SubmitField('Apply Filters')

class ClientForm(FlaskForm):
    """Form for creating/editing clients"""
    # Basic Information
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=255)])
    name = StringField('Contact Person Name', validators=[Optional(), Length(max=255)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    
    # Address Information
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    
    # Business Information
    client_type = SelectField('Client Type', 
                            choices=[('INDIVIDUAL', 'Individual'), ('COMPANY', 'Company')],
                            validators=[DataRequired()],
                            default='COMPANY')
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    vat_number = StringField('VAT Number', validators=[Optional(), Length(max=50)])
    registration_number = StringField('Registration Number', validators=[Optional(), Length(max=50)])
    website = StringField('Website', validators=[Optional(), Length(max=255)])
    
    # Additional Contact
    contact_person = StringField('Alternative Contact Person', validators=[Optional(), Length(max=255)])
    contact_email = EmailField('Alternative Contact Email', validators=[Optional(), Email(), Length(max=120)])
    contact_phone = StringField('Alternative Contact Phone', validators=[Optional(), Length(max=20)])
    
    # Package and Status Management
    package_id = SelectField('Package Plan', coerce=int, validators=[Optional()])
    client_status = SelectField('Client Status',
                              choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended'), ('pending', 'Pending Verification')],
                              validators=[DataRequired()],
                              default='active')
    is_verified = BooleanField('Account Verified', default=False)
    
    # Technical Settings
    rate_limit = IntegerField('API Rate Limit (req/min)', validators=[Optional(), NumberRange(min=1, max=10000)], default=100)
    theme_color = StringField('Theme Color', validators=[Optional(), Length(max=7)], default='#6c63ff')
    
    # Commission Settings
    deposit_commission_rate = DecimalField('Deposit Commission Rate (%)', 
                                         validators=[NumberRange(min=0, max=100)], 
                                         places=2,
                                         default=Decimal('3.5'))
    withdrawal_commission_rate = DecimalField('Withdrawal Commission Rate (%)', 
                                            validators=[NumberRange(min=0, max=100)], 
                                            places=2,
                                            default=Decimal('1.5'))
    
    # Account Balance Management
    balance = DecimalField('Account Balance', validators=[Optional(), NumberRange(min=0)], places=8, default=Decimal('0.0'))
    commission_balance = DecimalField('Commission Balance', validators=[Optional(), NumberRange(min=0)], places=8, default=Decimal('0.0'))
    
    # Status and Notes
    is_active = BooleanField('Active', default=True)
    notes = TextAreaField('Admin Notes', validators=[Optional()])
    
    # Login Credentials
    username = StringField('Client Username', validators=[Optional(), Length(min=4, max=50)])
    password = PasswordField('Client Password', validators=[Optional(), Length(min=8, max=128)])
    new_password = PasswordField('New Password (reset)', validators=[Optional(), Length(min=8, max=128)])
    auto_generate_password = BooleanField('Auto-generate new password', default=False)
    webhook_url = StringField('Webhook URL', validators=[Optional(), Length(max=500)])
    
    # API Management
    api_key_enabled = BooleanField('Enable API Access', default=True)
    auto_generate_api_key = BooleanField('Auto-generate new API key', default=False)
    
    submit = SubmitField('Save Client')
    
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        # Populate package choices dynamically
        from app.models.client_package import ClientPackage
        self.package_id.choices = [(0, 'No Package')] + [
            (pkg.id, f"{pkg.name} ({pkg.client_type.value})") 
            for pkg in ClientPackage.query.filter_by(status='active').order_by(ClientPackage.name).all()
        ]

class ClientFeatureForm(FlaskForm):
    """Form for managing client features independently"""
    client_id = HiddenField('Client ID', validators=[DataRequired()])
    submit = SubmitField('Update Features')
    
    def __init__(self, client=None, *args, **kwargs):
        super(ClientFeatureForm, self).__init__(*args, **kwargs)
        if client:
            self.client_id.data = client.id
            # Dynamically add feature checkboxes
            from app.models.client_package import Feature
            features = Feature.query.order_by(Feature.category, Feature.name).all()
            
            for feature in features:
                field_name = f'feature_{feature.id}'
                # Check if client currently has this feature
                has_feature = client.has_feature(feature.feature_key) if client else False
                setattr(self, field_name, BooleanField(
                    label=f"{feature.name}",
                    description=feature.description,
                    default=has_feature
                ))

class ApiKeyManagementForm(FlaskForm):
    """Form for managing client API keys"""
    client_id = HiddenField('Client ID', validators=[DataRequired()])
    key_name = StringField('Key Name', validators=[DataRequired(), Length(max=100)])
    permissions = SelectMultipleField('Permissions', 
                                    choices=[
                                        ('payments:read', 'Read Payments'),
                                        ('payments:write', 'Create Payments'),
                                        ('withdrawals:read', 'Read Withdrawals'),
                                        ('withdrawals:write', 'Create Withdrawals'),
                                        ('invoices:read', 'Read Invoices'),
                                        ('invoices:write', 'Create Invoices'),
                                        ('analytics:read', 'View Analytics'),
                                        ('webhooks:manage', 'Manage Webhooks')
                                    ])
    rate_limit = IntegerField('Rate Limit (req/min)', validators=[Optional(), NumberRange(min=1, max=1000)], default=60)
    expires_at = DateTimeField('Expires At', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create API Key')

class AdminUserForm(FlaskForm):
    """Form for creating/editing admin users"""
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                  validators=[DataRequired(), 
                                              EqualTo('password', message='Passwords must match')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Admin User')

class AdminWithdrawalActionForm(FlaskForm):
    """Form for admin actions on withdrawals"""
    action = SelectField(
        'Action',
        choices=[
            ('approve', 'Approve and Process'),
            ('reject', 'Reject')
        ],
        validators=[DataRequired()]
    )
    note = TextAreaField(
        'Admin Note',
        validators=[Optional(), Length(max=500)],
        render_kw={
            'placeholder': 'Add any notes about this action (visible to client)',
            'rows': 3
        }
    )
    submit = SubmitField('Confirm Action')

class WithdrawalFilterForm(FlaskForm):
    """Form for filtering withdrawal requests"""
    status = SelectField(
        'Status',
        choices=[
            ('all', 'All Statuses'),
            (WithdrawalStatus.PENDING.value, 'Pending'),
            (WithdrawalStatus.APPROVED.value, 'Approved'),
            (WithdrawalStatus.COMPLETED.value, 'Completed'),
            (WithdrawalStatus.REJECTED.value, 'Rejected'),
            (WithdrawalStatus.CANCELLED.value, 'Cancelled'),
            (WithdrawalStatus.FAILED.value, 'Failed')
        ],
        default=WithdrawalStatus.PENDING.value,
        validators=[DataRequired()]
    )
    client_id = StringField('Client ID', validators=[Optional()])
    date_from = StringField('From', validators=[Optional()], render_kw={"type": "date"})
    date_to = StringField('To', validators=[Optional()], render_kw={"type": "date"})
    submit = SubmitField('Apply Filters')

class TransactionSearchForm(FlaskForm):
    """Form for searching transactions"""
    tx_hash = StringField('Transaction Hash', validators=[Optional()])
    client_id = StringField('Client ID', validators=[Optional()])
    currency = StringField('Currency', validators=[Optional()])
    date_from = StringField('From', validators=[Optional()], render_kw={"type": "date"})
    date_to = StringField('To', validators=[Optional()], render_kw={"type": "date"})
    submit = SubmitField('Search')
