from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20, message='Username must be between 4 and 20 characters.')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UnitConverterForm(FlaskForm):
    """Unit converter form"""
    conversion_type = SelectField('Conversion Type', choices=[
        ('length', 'Length (Meters ↔ Feet)'),
        ('weight', 'Weight (Kg ↔ Tons)'),
        ('area', 'Area (Sq.m ↔ Sq.ft)'),
        ('volume', 'Volume (Cu.m ↔ Cu.ft)'),
        ('pressure', 'Pressure (N/mm² ↔ PSI)')
    ], validators=[DataRequired()])
    value = FloatField('Value', validators=[DataRequired()])
    from_unit = SelectField('From Unit', choices=[], validators=[DataRequired()])
    to_unit = SelectField('To Unit', choices=[], validators=[DataRequired()])
    submit = SubmitField('Convert')

class MaterialEstimatorForm(FlaskForm):
    """Material estimator form"""
    area = FloatField('Area (sq.m)', validators=[DataRequired()])
    construction_type = SelectField('Construction Type', choices=[
        ('brick_wall', 'Brick Wall (9 inch)'),
        ('concrete_slab', 'RCC Slab (6 inch)'),
        ('plaster', 'Plastering'),
        ('flooring', 'Flooring'),
        ('foundation', 'Foundation')
    ], validators=[DataRequired()])
    submit = SubmitField('Estimate Materials')