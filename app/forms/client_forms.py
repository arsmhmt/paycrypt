from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateField, FileField, BooleanField, PasswordField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo, URL
from app.models.enums import ClientEntityType

class ClientRegistrationForm(FlaskForm):
    # Package selection (hidden field, set from URL parameter)
    package_id = HiddenField('Package ID')

    # User fields
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=64, message='Username must be between 4 and 64 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120, message='Email cannot exceed 120 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired()
    ])


    # Client fields
    company_name = StringField('Company Name', validators=[
        DataRequired(),
        Length(max=255, message='Company name cannot exceed 255 characters')
    ])
    contact_person = StringField('Contact Person', validators=[Optional(), Length(max=255)])
    contact_email = StringField('Contact Email', validators=[Optional(), Email(), Length(max=120)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=20)])

    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    vat_number = StringField('VAT Number', validators=[Optional(), Length(max=50)])
    registration_number = StringField('Registration Number', validators=[Optional(), Length(max=50)])
    website = StringField('Website', validators=[Optional(), Length(max=255), URL(require_tld=True, message='Please enter a valid URL')])

    # Terms and Conditions
    accept_terms = BooleanField('I accept the Terms and Conditions', validators=[
        DataRequired(message='You must accept the terms and conditions')
    ])
    accept_privacy = BooleanField('I accept the Privacy Policy', validators=[
        DataRequired(message='You must accept the privacy policy')
    ])


class ClientDocumentUploadForm(FlaskForm):
    """Form for uploading client documents"""
    document_type = SelectField('Document Type', 
                              choices=[
                                  ('id_card', 'ID Card'),
                                  ('passport', 'Passport'),
                                  ('business_license', 'Business License'),
                                  ('other', 'Other')
                              ],
                              validators=[DataRequired()])
    document_description = TextAreaField('Description', validators=[Optional()])
    document_file = FileField('Document File', validators=[DataRequired()])
    is_primary = BooleanField('Primary Document')

class PaymentForm(FlaskForm):
    # Fiat currency and amount
    fiat_currency = SelectField(
        'Fiat Currency',
        choices=[
            ('USD', 'USD - US Dollar'),
            ('EUR', 'EUR - Euro'),
            ('GBP', 'GBP - British Pound'),
            ('TRY', 'TRY - Turkish Lira')
        ],
        validators=[DataRequired()],
        default='USD'
    )
    
    fiat_amount = DecimalField(
        'Amount',
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message='Amount must be greater than 0')
        ],
        render_kw={
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Enter amount in selected currency'
        }
    )
    
    # Crypto amount (readonly, will be calculated)
    crypto_amount = StringField(
        'Crypto Amount',
        render_kw={
            'readonly': True,
            'class': 'form-control-plaintext',
            'data-crypto-amount': ''
        }
    )
    
    # Hidden fields for the actual values
    crypto_currency = StringField(
        'Crypto Currency',
        default='BTC',
        render_kw={
            'readonly': True,
            'class': 'd-none'
        }
    )
    
    exchange_rate = StringField(
        'Exchange Rate',
        render_kw={
            'readonly': True,
            'class': 'd-none',
            'data-exchange-rate': ''
        }
    )
    
    rate_expiry = StringField(
        'Rate Expiry',
        render_kw={
            'readonly': True,
            'class': 'd-none',
            'data-rate-expiry': ''
        }
    )
    
    # Payment method and reference
    payment_method = SelectField(
        'Payment Method',
        choices=[
            ('bank_transfer', 'Bank Transfer'),
            ('credit_card', 'Credit Card'),
            ('crypto', 'Cryptocurrency')
        ],
        validators=[DataRequired()],
        default='bank_transfer'
    )
    
    reference = StringField(
        'Reference/Note',
        validators=[
            Optional(),
            Length(max=255, message='Reference cannot exceed 255 characters')
        ],
        render_kw={
            'placeholder': 'Optional payment reference or note'
        }
    )
    
    document = FileField(
        'Upload Payment Proof',
        validators=[
            Optional(),
            # Add file validation if needed
        ]
    )
    
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        # Set default crypto currency
        self.crypto_currency.data = 'BTC'
        
    def validate(self, **kwargs):
        # Run standard validation first
        if not super().validate():
            return False
            
        # Additional validation can be added here if needed
        return True

class InvoiceForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    currency = SelectField('Currency', 
                         choices=[('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP')],
                         validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])

class DocumentUploadForm(FlaskForm):
    document_type = SelectField('Document Type', 
                              choices=[('payment_proof', 'Payment Proof'),
                                       ('company_docs', 'Company Documents'),
                                       ('other', 'Other')],
                              validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])

class NotificationPreferenceForm(FlaskForm):
    email_notifications = BooleanField('Email Notifications')
    sms_notifications = BooleanField('SMS Notifications')
    push_notifications = BooleanField('Push Notifications')
    payment_updates = BooleanField('Payment Status Updates')
    invoice_reminders = BooleanField('Invoice Reminders')
    system_alerts = BooleanField('System Alerts')


class ClientApiKeyForm(FlaskForm):
    """Form for creating a new API key with client type awareness"""
    name = StringField('API Key Name', validators=[
        DataRequired(), 
        Length(min=1, max=100, message='Name must be between 1 and 100 characters')
    ])
    
    # Rate limiting - different limits based on client type
    rate_limit = IntegerField('Rate Limit (requests per minute)', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000, message='Rate limit must be between 1 and 1000 requests per minute')
    ], default=60)
    
    # Optional expiry
    expires_in_days = SelectField('Expires In', choices=[
        ('', 'Never'),
        ('30', '30 days'),
        ('90', '90 days'),
        ('180', '6 months'),
        ('365', '1 year')
    ], validators=[Optional()])
    
    # Commission-Based Client Permissions (limited)
    perm_commission_payment_create = BooleanField('Create Payments')
    perm_commission_payment_read = BooleanField('Read Payments')
    perm_commission_balance_read = BooleanField('Read Balance')
    perm_commission_status_check = BooleanField('Check Status')
    
    # Flat-Rate Client Permissions (full suite)
    perm_flat_rate_payment_create = BooleanField('Create Payments')
    perm_flat_rate_payment_read = BooleanField('Read Payments')
    perm_flat_rate_payment_update = BooleanField('Update Payments')
    perm_flat_rate_withdrawal_create = BooleanField('Create Withdrawals')
    perm_flat_rate_withdrawal_read = BooleanField('Read Withdrawals')
    perm_flat_rate_withdrawal_approve = BooleanField('Approve Withdrawals')
    perm_flat_rate_balance_read = BooleanField('Read Balance')
    perm_flat_rate_balance_update = BooleanField('Update Balance')
    perm_flat_rate_wallet_manage = BooleanField('Manage Wallets')
    perm_flat_rate_webhook_manage = BooleanField('Manage Webhooks')
    perm_flat_rate_user_manage = BooleanField('Manage Users')
    perm_flat_rate_invoice_create = BooleanField('Create Invoices')
    perm_flat_rate_invoice_read = BooleanField('Read Invoices')
    perm_flat_rate_profile_read = BooleanField('Read Profile')
    perm_flat_rate_profile_update = BooleanField('Update Profile')
    
    # IP Restriction for Flat-Rate clients (Enterprise feature)
    allowed_ips = StringField('Allowed IP Addresses', validators=[Optional()], 
                             render_kw={'placeholder': '192.168.1.1,203.0.113.1 (comma-separated)'})


class ClientApiKeyEditForm(FlaskForm):
    """Form for editing an existing API key"""
    name = StringField('API Key Name', validators=[
        DataRequired(), 
        Length(min=1, max=100, message='Name must be between 1 and 100 characters')
    ])
    
    # Rate limiting
    rate_limit = IntegerField('Rate Limit (requests per minute)', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000, message='Rate limit must be between 1 and 1000 requests per minute')
    ])
    
    # Status
    is_active = BooleanField('Active')
    
    # Commission-Based Client Permissions (limited)
    perm_commission_payment_create = BooleanField('Create Payments')
    perm_commission_payment_read = BooleanField('Read Payments')
    perm_commission_balance_read = BooleanField('Read Balance')
    perm_commission_status_check = BooleanField('Check Status')
    
    # Flat-Rate Client Permissions (full suite)
    perm_flat_rate_payment_create = BooleanField('Create Payments')
    perm_flat_rate_payment_read = BooleanField('Read Payments')
    perm_flat_rate_payment_update = BooleanField('Update Payments')
    perm_flat_rate_withdrawal_create = BooleanField('Create Withdrawals')
    perm_flat_rate_withdrawal_read = BooleanField('Read Withdrawals')
    perm_flat_rate_withdrawal_approve = BooleanField('Approve Withdrawals')
    perm_flat_rate_balance_read = BooleanField('Read Balance')
    perm_flat_rate_balance_update = BooleanField('Update Balance')
    perm_flat_rate_wallet_manage = BooleanField('Manage Wallets')
    perm_flat_rate_webhook_manage = BooleanField('Manage Webhooks')
    perm_flat_rate_user_manage = BooleanField('Manage Users')
    perm_flat_rate_invoice_create = BooleanField('Create Invoices')
    perm_flat_rate_invoice_read = BooleanField('Read Invoices')
    perm_flat_rate_profile_read = BooleanField('Read Profile')
    perm_flat_rate_profile_update = BooleanField('Update Profile')
    
    # IP Restriction for Flat-Rate clients
    allowed_ips = StringField('Allowed IP Addresses', validators=[Optional()], 
                             render_kw={'placeholder': '192.168.1.1,203.0.113.1 (comma-separated)'})


class ClientApiKeyRevokeForm(FlaskForm):
    """Form for revoking an API key"""
    api_key_id = HiddenField(validators=[DataRequired()])
    confirm_revoke = BooleanField('I confirm that I want to revoke this API key', validators=[DataRequired()])


class WebhookConfigForm(FlaskForm):
    """Form for webhook configuration (Flat-Rate clients only)"""
    name = StringField('Webhook Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    
    url = StringField('Webhook URL', validators=[
        DataRequired(),
        Length(max=255),
        # Add URL validation if needed
    ], render_kw={'placeholder': 'https://yourapi.com/webhooks/paycrypt'})
    
    events = SelectField('Events to Send', choices=[
        ('payment.created', 'Payment Created'),
        ('payment.confirmed', 'Payment Confirmed'),
        ('payment.failed', 'Payment Failed'),
        ('withdrawal.created', 'Withdrawal Created'),
        ('withdrawal.approved', 'Withdrawal Approved'),
        ('withdrawal.rejected', 'Withdrawal Rejected'),
        ('balance.updated', 'Balance Updated'),
        ('all', 'All Events')
    ], validators=[DataRequired()])
    
    is_active = BooleanField('Active', default=True)
    
    # Secret for HMAC verification
    secret = StringField('Webhook Secret', validators=[Optional()],
                        render_kw={'placeholder': 'Leave empty to auto-generate'})
    
    # Retry configuration
    max_retries = IntegerField('Max Retries', validators=[
        NumberRange(min=0, max=10)
    ], default=3)
    
    timeout_seconds = IntegerField('Timeout (seconds)', validators=[
        NumberRange(min=5, max=60)
    ], default=30)
