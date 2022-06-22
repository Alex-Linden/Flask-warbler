from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, URL, Optional


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class UserEditForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[Optional()])
    email = StringField('E-mail', validators=[Optional(), Email()])
    image_url = StringField(
                            '(Optional) Profile Image URL',
                            validators=[Optional(),URL()])
    header_image_url = StringField(
                                    '(Optional) Header Image URL',
                                    validators=[Optional(),URL()])
    bio = TextAreaField('text', validators=[Optional()])
    password = PasswordField('Password', validators=[Length(min=6)])




class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""
