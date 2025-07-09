from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User
from app.models.role import Role

class UserForm(FlaskForm):
    """Form for creating and editing users"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    first_name = StringField('First Name', validators=[
        Length(max=50)
    ])
    last_name = StringField('Last Name', validators=[
        Length(max=50)
    ])
    password = PasswordField('Password', validators=[])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    is_active = BooleanField('Active', default=True)
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(r.id, r.name) for r in Role.query.order_by('name').all()]

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and (not hasattr(self, 'user') or user.id != self.user.id):
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (not hasattr(self, 'user') or user.id != self.user.id):
            raise ValidationError('That email is already registered. Please use a different one.')


class RoleForm(FlaskForm):
    """Form for creating and editing roles"""
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])
    description = TextAreaField('Description', validators=[
        Length(max=255)
    ])
    permissions = SelectField('Permissions', 
        choices=[
            ('admin', 'Admin - Full access'),
            ('manage_users', 'Manage Users - Can manage users and roles'),
            ('manage_clients', 'Manage Clients - Can manage clients'),
            ('view_reports', 'View Reports - Can view reports'),
            ('basic', 'Basic - Limited access')
        ],
        multiple=True,
        validators=[DataRequired()]
    )
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        if not self.permissions.data:
            self.permissions.data = []

    def validate_name(self, name):
        role = Role.query.filter_by(name=name.data).first()
        if role and (not hasattr(self, 'role') or role.id != self.role.id):
            raise ValidationError('A role with that name already exists.')
