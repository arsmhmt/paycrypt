from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, HiddenField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, URL, ValidationError, Regexp
from flask_login import current_user
from app.models import User

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    # Personal Information
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name cannot exceed 50 characters')
    ], render_kw={"placeholder": "Your first name"})
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name cannot exceed 50 characters')
    ], render_kw={"placeholder": "Your last name"})
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=4, max=25, message='Username must be between 4 and 25 characters'),
        Regexp('^[A-Za-z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ], render_kw={"placeholder": "Choose a username"})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(max=120, message='Email cannot exceed 120 characters')
    ], render_kw={"placeholder": "your.email@example.com"})
    
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required'),
        Length(min=10, max=20, message='Phone number must be between 10 and 20 characters')
    ], render_kw={"placeholder": "+1 (123) 456-7890"})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp('(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+\-=[\]{};\'\"|,.<>/?]).{8,}', 
               message='Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character')
    ], render_kw={"placeholder": "Create a strong password"})
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={"placeholder": "Retype your password"})
    
    # Package information
    package_id = HiddenField('Package ID', validators=[
        DataRequired()
    ])
    
    # Company information
    company_name = StringField('Company Name', validators=[
        DataRequired(),
        Length(max=255, message='Company name cannot exceed 255 characters')
    ])
    
    tax_id = StringField('Tax ID', validators=[
        Optional(),
        Length(max=50, message='Tax ID cannot exceed 50 characters')
    ])
    
    vat_number = StringField('VAT Number', validators=[
        Optional(),
        Length(max=50, message='VAT number cannot exceed 50 characters')
    ])
    
    website = StringField('Website', validators=[
        Optional(),
        URL(message='Please enter a valid URL'),
        Length(max=255, message='Website URL cannot exceed 255 characters')
    ])
    
    # Contact Information
    contact_person = StringField('Contact Person', validators=[
        DataRequired(),
        Length(max=100, message='Contact person name cannot exceed 100 characters')
    ])
    
    contact_email = StringField('Contact Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120, message='Email cannot exceed 120 characters')
    ])
    
    contact_phone = StringField('Contact Phone', validators=[
        DataRequired(),
        Length(max=20, message='Phone number cannot exceed 20 characters')
    ])
    
    # Address Information
    address = StringField('Address', validators=[
        DataRequired(message='Address is required'),
        Length(max=200, message='Address cannot exceed 200 characters')
    ], render_kw={"placeholder": "123 Main St"})
    
    city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(max=100, message='City name cannot exceed 100 characters')
    ], render_kw={"placeholder": "New York"})
    
    state = StringField('State/Province', validators=[
        Optional(),
        Length(max=100, message='State/Province cannot exceed 100 characters')
    ], render_kw={"placeholder": "New York (Optional)"})
    
    postal_code = StringField('Postal/ZIP Code', validators=[
        DataRequired(message='Postal/ZIP code is required'),
        Length(max=20, message='Postal/ZIP code cannot exceed 20 characters')
    ], render_kw={"placeholder": "10001"})
    
    country = StringField('Country', validators=[
        DataRequired(),
        Length(max=100, message='Country name cannot exceed 100 characters')
    ])
    
    # Terms and Conditions
    accept_terms = BooleanField('I accept the Terms and Conditions', validators=[
        DataRequired(message='You must accept the Terms and Conditions')
    ])
    
    # Marketing preferences
    subscribe_newsletter = BooleanField('Subscribe to our newsletter', default=False)
    
    # Privacy consent
    accept_privacy = BooleanField('I consent to receive marketing communications', default=False)
    
    # Submit button
    submit = SubmitField('Create Account')
    
    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ForgotPasswordForm(FlaskForm):
    """Form for requesting a password reset"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """Form for resetting a password"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired()
    ])
    
    submit = SubmitField('Reset Password')


class VerifyEmailForm(FlaskForm):
    """Form for verifying email address"""
    token = HiddenField('Verification Token', validators=[
        DataRequired()
    ])
    submit = SubmitField('Verify Email')
