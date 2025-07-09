from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Optional, NumberRange

class AdminWithdrawalActionForm(FlaskForm):
    """Form for admin actions on withdrawals (approve/reject)."""
    action = SelectField(
        'Action',
        choices=[
            ('approve', 'Approve'),
            ('reject', 'Reject')
        ],
        validators=[DataRequired()]
    )
    admin_note = TextAreaField('Admin Note', validators=[Optional()])
    submit = SubmitField('Submit')
