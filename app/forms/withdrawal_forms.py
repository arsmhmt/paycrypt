from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app.models import WithdrawalRequest, WithdrawalStatus

class WithdrawalForm(FlaskForm):
    amount = FloatField(
        'Amount',
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Amount must be greater than 0.01")
        ]
    )
    crypto_address = StringField(
        'Crypto Address',
        validators=[DataRequired()]
    )
    currency = SelectField(
        'Currency',
        choices=[
            ('USDT', 'USDT'),
            ('BTC', 'BTC'),
            ('ETH', 'ETH'),
            ('BNB', 'BNB')
        ],
        default='USDT'
    )
    submit = SubmitField('Request Withdrawal')
    
    def validate_amount(self, field):
        """Validate withdrawal amount against available balance"""
        if field.data > self.client.available_balance:
            raise ValidationError(
                f"Insufficient balance. Available balance: {self.client.available_balance}"
            )
    
    def validate_crypto_address(self, field):
        """Validate crypto address format"""
        if not validate_crypto_address(field.data, self.currency.data):
            raise ValidationError("Invalid crypto address format")
