from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, TextAreaField, DecimalField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError
from app.models import Client, AdminUser

class ClientForm(FlaskForm):
    """Form for creating and editing clients"""
    # Basic Information
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=255)])
    name = StringField('Contact Person Name', validators=[Optional(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
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
    contact_email = StringField('Alternative Contact Email', validators=[Optional(), Email(), Length(max=120)])
    contact_phone = StringField('Alternative Contact Phone', validators=[Optional(), Length(max=20)])
    
    # Technical Settings
    rate_limit = IntegerField('API Rate Limit (req/min)', validators=[Optional(), NumberRange(min=1, max=10000)], default=100)
    theme_color = StringField('Theme Color', validators=[Optional(), Length(max=7)], default='#6c63ff')
    webhook_url = StringField('Webhook URL', validators=[Optional(), Length(max=500)])
    
    # Commission Settings
    deposit_commission_rate = FloatField('Deposit Commission (%)', 
                                       validators=[NumberRange(min=0, max=100)], 
                                       default=3.5)
    withdrawal_commission_rate = FloatField('Withdrawal Commission (%)', 
                                          validators=[NumberRange(min=0, max=100)], 
                                          default=1.5)
    
    # Status and Notes
    is_active = BooleanField('Active', default=True)
    notes = TextAreaField('Notes', validators=[Optional()])

    # Login Credentials
    username = StringField('Client Username', validators=[Optional(), Length(min=4, max=50)])
    password = PasswordField('Client Password', validators=[Optional(), Length(min=8, max=128)])
    new_password = PasswordField('New Password (reset)', validators=[Optional(), Length(min=8, max=128)])
    auto_generate_password = BooleanField('Auto-generate new password', default=False)

class AdminUserForm(FlaskForm):
    """Form for creating and editing admin users"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password')
    is_active = BooleanField('Active', default=True)

    def validate_username(self, username):
        """Check if username is already taken"""
        admin = AdminUser.query.filter_by(username=username.data).first()
        if admin and (not hasattr(self, 'admin') or admin.id != self.admin.id):
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email is already in use"""
        admin = AdminUser.query.filter_by(email=email.data).first()
        if admin and (not hasattr(self, 'admin') or admin.id != self.admin.id):
            raise ValidationError('This email is already registered. Please use a different one.')

    def validate_confirm_password(self, field):
        """Check if passwords match"""
        if self.password.data and self.password.data != field.data:
            raise ValidationError('Passwords must match')

class PaymentFilterForm(FlaskForm):
    """Form for filtering payments"""
    status = SelectField('Status', 
        choices=[
            ('all', 'All Statuses'),
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded')
        ],
        default='all'
    )
    client_id = SelectField('Client', coerce=int, validators=[Optional()])
    search = StringField('Search', validators=[Optional()])
    start_date = DateField('From', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('To', format='%Y-%m-%d', validators=[Optional()])

class WithdrawalActionForm(FlaskForm):
    """Form for approving/rejecting withdrawals"""
    action = SelectField('Action', 
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject')
        ],
        validators=[DataRequired()]
    )
    admin_note = TextAreaField('Admin Note', validators=[Optional(), Length(max=500)])

class TransactionSearchForm(FlaskForm):
    """Form for searching transactions"""
    transaction_id = StringField('Transaction ID', validators=[Optional()])
    reference = StringField('Reference', validators=[Optional()])
    status = SelectField('Status', 
        choices=[
            ('', 'All Statuses'),
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='',
        validators=[Optional()]
    )
    start_date = DateField('From', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('To', format='%Y-%m-%d', validators=[Optional()])
