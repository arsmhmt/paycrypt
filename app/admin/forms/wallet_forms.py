from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, DecimalField, IntegerField, HiddenField, validators
from wtforms.validators import DataRequired, Optional, Length, Email, NumberRange, URL, ValidationError
from app.models import db, WalletProvider, WalletProviderCurrency, WalletProviderType

class WalletProviderForm(FlaskForm):
    """Form for creating and editing wallet providers."""
    name = StringField('Provider Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    
    type = SelectField('Provider Type', 
        choices=[(t.value, t.name.replace('_', ' ').title()) for t in WalletProviderType],
        validators=[DataRequired()],
        coerce=str
    )
    
    api_key = StringField('API Key', validators=[
        DataRequired(),
        Length(min=10)
    ])
    
    api_secret = PasswordField('API Secret', validators=[
        DataRequired(),
        Length(min=10)
    ])
    
    api_url = StringField('API URL', validators=[
        DataRequired(),
        URL(),
        Length(max=255)
    ])
    
    is_active = BooleanField('Active', default=True)
    is_primary = BooleanField('Set as Primary', default=False)
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    
    config = TextAreaField('Configuration (JSON)', validators=[
        Optional(),
        Length(max=2000)
    ], 
    render_kw={"rows": 8, "placeholder": "Enter additional configuration as JSON..."})
    
    def validate_config(self, field):
        """Validate that the config field contains valid JSON if provided."""
        if field.data:
            try:
                import json
                json.loads(field.data)
            except ValueError as e:
                raise ValidationError('Invalid JSON configuration')


class WalletProviderCurrencyForm(FlaskForm):
    """Form for adding/editing wallet provider currencies."""
    currency_code = StringField('Currency Code', validators=[
        DataRequired(),
        Length(min=3, max=10)
    ])
    
    is_default = BooleanField('Default Currency', default=False)
    
    min_withdrawal = DecimalField('Minimum Withdrawal', validators=[
        DataRequired(),
        NumberRange(min=0)
    ], places=8)
    
    withdrawal_fee = DecimalField('Withdrawal Fee', validators=[
        DataRequired(),
        NumberRange(min=0)
    ], places=8)
    
    fee_type = SelectField('Fee Type', 
        choices=[
            ('fixed', 'Fixed Amount'),
            ('percentage', 'Percentage')
        ],
        validators=[DataRequired()],
        default='fixed'
    )
    
    is_active = BooleanField('Active', default=True)
    
    config = TextAreaField('Currency Configuration (JSON)', validators=[
        Optional(),
        Length(max=1000)
    ],
    render_kw={"rows": 5, "placeholder": "Enter currency-specific configuration as JSON..."})
    
    def validate_currency_code(self, field):
        """Validate that currency code is unique for this provider."""
        provider_id = getattr(self, '_provider_id', None)
        
        query = db.session.query(WalletProviderCurrency).filter_by(
            currency_code=field.data.upper()
        )
        
        if provider_id:
            query = query.filter(WalletProviderCurrency.provider_id != provider_id)
            
        if query.first() is not None:
            raise ValidationError('This currency is already configured for this provider')
    
    def validate_config(self, field):
        """Validate that the config field contains valid JSON if provided."""
        if field.data:
            try:
                import json
                json.loads(field.data)
            except ValueError as e:
                raise ValidationError('Invalid JSON configuration')


class WalletTransactionFilterForm(FlaskForm):
    """Form for filtering wallet transactions."""
    transaction_type = SelectField('Transaction Type', 
        choices=[
            ('', 'All Types'),
            ('deposit', 'Deposit'),
            ('withdrawal', 'Withdrawal'),
            ('fee', 'Fee'),
            ('adjustment', 'Adjustment')
        ],
        validators=[Optional()]
    )
    
    status = SelectField('Status',
        choices=[
            ('', 'All Statuses'),
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled')
        ],
        validators=[Optional()]
    )
    
    currency = SelectField('Currency', validators=[Optional()])
    
    date_from = StringField('From Date', validators=[Optional()], 
                          render_kw={"class": "datepicker", "placeholder": "YYYY-MM-DD"})
    
    date_to = StringField('To Date', validators=[Optional()],
                        render_kw={"class": "datepicker", "placeholder": "YYYY-MM-DD"})
    
    sort_by = SelectField('Sort By',
        choices=[
            ('created_at_desc', 'Newest First'),
            ('created_at_asc', 'Oldest First'),
            ('amount_desc', 'Amount (High to Low)'),
            ('amount_asc', 'Amount (Low to High)')
        ],
        default='created_at_desc'
    )
