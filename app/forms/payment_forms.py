from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, DecimalField, TextAreaField, SubmitField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, Optional, ValidationError
from app.utils.crypto_config import get_cryptocurrency_choices

class PaymentMethodFieldsForm(FlaskForm):
    # Credit Card Fields
    card_number = StringField('Card Number', 
        validators=[
            Length(min=15, max=19),
            Regexp(r'^\d+$', message='Card number must contain only digits')
        ])
    expiry_date = StringField('Expiry Date', 
        validators=[
            Regexp(r'^\d{2}/\d{2}$', message='Expiry date must be in MM/YY format')
        ])
    cvv = PasswordField('CVV', 
        validators=[
            Length(min=3, max=4),
            Regexp(r'^\d+$', message='CVV must contain only digits')
        ])
    card_holder_name = StringField('Card Holder Name', validators=[DataRequired()])
    card_type = SelectField('Card Type', choices=[
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('discover', 'Discover')
    ])

    # Bank Transfer Fields
    bank_account_number = StringField('Bank Account Number', validators=[DataRequired()])
    bank_name = StringField('Bank Name', validators=[DataRequired()])
    bank_branch = StringField('Bank Branch')
    swift_code = StringField('SWIFT/BIC Code')
    iban = StringField('IBAN')

    # Cash Fields
    payment_location = StringField('Payment Location', validators=[DataRequired()])
    cash_collected_by = StringField('Collected By', validators=[DataRequired()])
    cash_receipt_number = StringField('Receipt Number')

    # Other Payment Fields
    other_payment_method = StringField('Payment Method', validators=[DataRequired()])
    other_payment_details = StringField('Payment Details', validators=[DataRequired()])


class PaymentForm(FlaskForm):
    """Form for creating and updating payments"""
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    currency = SelectField('Currency', choices=[
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('TRY', 'TRY - Turkish Lira')
    ], default='USD')
    description = TextAreaField('Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    payment_method = SelectField('Payment Method', choices=[
        ('bitcoin', 'Bitcoin'),
        ('ethereum', 'Ethereum'),
        ('litecoin', 'Litecoin'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other')
    ])
    transaction_id = StringField('Transaction ID', validators=[Optional()])
    submit = SubmitField('Save Payment')


class AdminPaymentForm(FlaskForm):
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    currency = StringField('Currency', validators=[DataRequired()])
    status = SelectField('Status', choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Create Payment')


class CryptocurrencySelectionForm(FlaskForm):
    """Form for selecting cryptocurrency for package activation payment"""
    cryptocurrency = SelectField(
        'Select Cryptocurrency',
        choices=[],  # Will be populated dynamically
        validators=[DataRequired(message='Please select a cryptocurrency')]
    )
    submit = SubmitField('Continue to Payment')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices with supported cryptocurrencies
        self.cryptocurrency.choices = get_cryptocurrency_choices()

class PackageActivationPaymentForm(FlaskForm):
    """Form for package activation payment confirmation"""
    package_id = HiddenField('Package ID', validators=[DataRequired()])
    cryptocurrency = HiddenField('Cryptocurrency', validators=[DataRequired()])
    amount = HiddenField('Amount', validators=[DataRequired()])
    address = HiddenField('Address', validators=[DataRequired()])
    
    # For demo purposes
    simulate_payment = SubmitField('Simulate Payment (Demo)', render_kw={'class': 'btn btn-warning'})
    
    def validate_cryptocurrency(self, field):
        """Validate that the cryptocurrency is supported"""
        from app.utils.crypto_config import get_cryptocurrency_info
        if not get_cryptocurrency_info(field.data):
            raise ValidationError('Unsupported cryptocurrency selected.')
