from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SelectField, BooleanField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError

# Define enum values directly to avoid circular imports
PLAN_TYPES = [
    ('standard', 'Standard'),
    ('premium', 'Premium'),
    ('enterprise', 'Enterprise'),
    ('custom', 'Custom')
]

BILLING_CYCLES = [
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('biannual', 'Biannual'),
    ('annual', 'Annual'),
    ('one_time', 'One Time')
]

class PricingPlanForm(FlaskForm):
    """Form for creating and editing pricing plans."""
    name = StringField('Plan Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    plan_type = SelectField('Plan Type', 
                          choices=PLAN_TYPES,
                          validators=[DataRequired()], 
                          coerce=str)
    billing_cycle = SelectField('Billing Cycle', 
                              choices=BILLING_CYCLES,
                              validators=[DataRequired()], 
                              coerce=str)
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    currency = StringField('Currency', validators=[DataRequired(), Length(min=3, max=3)])
    is_active = BooleanField('Active', default=True)
    features = TextAreaField('Features (one per line)', validators=[Optional()])
    
    def validate_currency(self, field):
        if len(field.data) != 3 or not field.data.isalpha():
            raise ValidationError('Currency must be a 3-letter currency code (e.g., USD, EUR)')

class PricingPlanFilterForm(FlaskForm):
    """Form for filtering pricing plans."""
    name = StringField('Plan Name', validators=[Optional()])
    plan_type = SelectField('Plan Type', 
                          choices=[('', 'All')] + PLAN_TYPES,
                          validators=[Optional()], 
                          coerce=str)
    billing_cycle = SelectField('Billing Cycle', 
                              choices=[('', 'All')] + BILLING_CYCLES,
                              validators=[Optional()], 
                              coerce=str)
    is_active = SelectField('Status', 
                          choices=[('', 'All'), ('1', 'Active'), ('0', 'Inactive')],
                          validators=[Optional()],
                          coerce=str)
    sort_by = SelectField('Sort By',
                         choices=[('name', 'Name (A-Z)'), 
                                ('-name', 'Name (Z-A)'),
                                ('price', 'Price (Low to High)'),
                                ('-price', 'Price (High to Low)')],
                         default='name',
                         validators=[Optional()])
    
    def validate(self, extra_validators=None):
        # Skip validation if no filters are applied
        if not any([self.name.data, self.plan_type.data, self.billing_cycle.data, self.is_active.data]):
            return True
        return super().validate(extra_validators)
