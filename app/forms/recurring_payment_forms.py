from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length
from app.models.recurring_payment import RecurringFrequency

class RecurringPaymentForm(FlaskForm):
    client_id = SelectField('Client', validators=[DataRequired()], coerce=int)
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    currency = SelectField('Currency', choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
        ('JPY', 'JPY'),
        ('AUD', 'AUD')
    ], validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        (f.value, f.name.title()) for f in RecurringFrequency
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date')
    payment_method = SelectField('Payment Method', choices=[
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    payment_provider = SelectField('Payment Provider')
    description = TextAreaField('Description', validators=[Length(max=255)])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled')
    ])

    def validate_end_date(self, field):
        if field.data and field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')
