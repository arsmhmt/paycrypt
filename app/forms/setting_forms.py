from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from app.models.setting import SettingType, SettingKey

class SettingForm(FlaskForm):
    """Form for editing settings"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = {}
        
        # Add fields based on setting type
        setting_type = kwargs.get('setting_type')
        if setting_type == SettingType.SYSTEM.value:
            self._add_system_fields()
        elif setting_type == SettingType.PAYMENT.value:
            self._add_payment_fields()
        elif setting_type == SettingType.NOTIFICATION.value:
            self._add_notification_fields()
        elif setting_type == SettingType.SECURITY.value:
            self._add_security_fields()
        elif setting_type == SettingType.EMAIL.value:
            self._add_email_fields()
        elif setting_type == SettingType.INTEGRATION.value:
            self._add_integration_fields()
        
    def _add_system_fields(self):
        """Add system settings fields"""
        self.fields[SettingKey.SYSTEM_NAME.value] = StringField(
            'System Name',
            validators=[DataRequired(), Length(max=100)]
        )
        self.fields[SettingKey.SYSTEM_TIMEZONE.value] = SelectField(
            'Timezone',
            choices=[
                ('UTC', 'UTC'),
                ('America/New_York', 'Eastern Time'),
                ('Europe/London', 'London'),
                ('Asia/Tokyo', 'Tokyo')
            ]
        )
        self.fields[SettingKey.SYSTEM_CURRENCY.value] = SelectField(
            'Default Currency',
            choices=[
                ('USD', 'US Dollar'),
                ('EUR', 'Euro'),
                ('GBP', 'British Pound'),
                ('JPY', 'Japanese Yen')
            ]
        )

    def _add_payment_fields(self):
        """Add payment settings fields"""
        self.fields[SettingKey.PAYMENT_CURRENCIES.value] = StringField(
            'Supported Currencies',
            description='Comma-separated list of currency codes (e.g., USD,EUR,GBP)'
        )
        self.fields[SettingKey.PAYMENT_METHODS.value] = StringField(
            'Payment Methods',
            description='Comma-separated list of payment methods (e.g., credit_card,bank_transfer,paypal)'
        )
        self.fields[SettingKey.MIN_PAYMENT_AMOUNT.value] = FloatField(
            'Minimum Payment Amount',
            validators=[NumberRange(min=0)],
            default=0.01
        )
        self.fields[SettingKey.MAX_PAYMENT_AMOUNT.value] = FloatField(
            'Maximum Payment Amount',
            validators=[NumberRange(min=0)],
            default=100000.00
        )

    def _add_notification_fields(self):
        """Add notification settings fields"""
        self.fields[SettingKey.EMAIL_PROVIDER.value] = SelectField(
            'Email Provider',
            choices=[
                ('smtp', 'SMTP'),
                ('sendgrid', 'SendGrid'),
                ('ses', 'Amazon SES')
            ]
        )
        self.fields[SettingKey.SMS_PROVIDER.value] = SelectField(
            'SMS Provider',
            choices=[
                ('twilio', 'Twilio'),
                ('nexmo', 'Nexmo'),
                ('plivo', 'Plivo')
            ]
        )
        self.fields[SettingKey.DEFAULT_NOTIFICATION_METHOD.value] = SelectField(
            'Default Notification Method',
            choices=[
                ('email', 'Email'),
                ('sms', 'SMS'),
                ('push', 'Push Notification')
            ]
        )

    def _add_security_fields(self):
        """Add security settings fields"""
        self.fields[SettingKey.PASSWORD_MIN_LENGTH.value] = IntegerField(
            'Minimum Password Length',
            validators=[NumberRange(min=4, max=100)],
            default=8
        )
        self.fields[SettingKey.PASSWORD_EXPIRY_DAYS.value] = IntegerField(
            'Password Expiry Days',
            validators=[NumberRange(min=1, max=365)],
            default=90
        )
        self.fields[SettingKey.LOGIN_ATTEMPT_LIMIT.value] = IntegerField(
            'Login Attempt Limit',
            validators=[NumberRange(min=1, max=20)],
            default=5
        )

    def _add_email_fields(self):
        """Add email settings fields"""
        self.fields[SettingKey.SMTP_SERVER.value] = StringField(
            'SMTP Server',
            validators=[DataRequired()]
        )
        self.fields[SettingKey.SMTP_PORT.value] = IntegerField(
            'SMTP Port',
            validators=[NumberRange(min=1, max=65535)],
            default=587
        )
        self.fields[SettingKey.SMTP_USERNAME.value] = StringField(
            'SMTP Username',
            validators=[Optional()]
        )
        self.fields[SettingKey.SMTP_PASSWORD.value] = PasswordField(
            'SMTP Password',
            validators=[Optional()]
        )

    def _add_integration_fields(self):
        """Add integration settings fields"""
        self.fields[SettingKey.PAYCRYPT_WALLET_ADDRESS.value] = StringField(
            'Paycrypt Wallet Address',
            validators=[Optional()]
        )
        self.fields[SettingKey.PAYCRYPT_API_KEY.value] = StringField(
            'Paycrypt API Key',
            validators=[Optional()]
        )

    def validate(self):
        """Validate all fields"""
        if not super().validate():
            return False
            
        # Validate payment amount ranges
        min_amount = self.fields[SettingKey.MIN_PAYMENT_AMOUNT.value].data
        max_amount = self.fields[SettingKey.MAX_PAYMENT_AMOUNT.value].data
        if min_amount and max_amount and min_amount > max_amount:
            self.fields[SettingKey.MIN_PAYMENT_AMOUNT.value].errors.append(
                'Minimum amount cannot be greater than maximum amount'
            )
            return False
            
        return True

    def get_settings(self):
        """Get all settings as a dictionary"""
        settings = {}
        for key, field in self.fields.items():
            settings[key] = field.data
        return settings
