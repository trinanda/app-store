from flask import url_for
from flask_babel import _, lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields import BooleanField, PasswordField, StringField, SubmitField

from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from app.models import User


class LoginForm(FlaskForm):
    email_or_phone_number = StringField(_l('Email or phone number'), validators=[InputRequired()])
    password = PasswordField(_l('Password'), validators=[InputRequired()])
    remember_me = BooleanField(_l('Keep me logged in'))
    submit = SubmitField(_l('Log in'))


class RegistrationForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(_l('Last name'), validators=[InputRequired(), Length(1, 64)])
    email = EmailField(_l('Email'), validators=[InputRequired(), Length(1, 64), Email()])
    password = PasswordField(_l('Password'), validators=[InputRequired(), EqualTo('password2', 'Passwords must match')])
    password2 = PasswordField(_l('Confirm password'), validators=[InputRequired()])
    submit = SubmitField(_l('Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. (Did you mean to <a href="{}">log in</a> instead?)'.format(
                url_for('account.login')))


class RequestResetPasswordForm(FlaskForm):
    email = EmailField(_l('Email'), validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField(_l('Reset password'))

    # We don't validate the email address so we don't confirm to attackers
    # that an account with the given email exists.


class ResetPasswordForm(FlaskForm):
    email = EmailField(_l('Email'), validators=[InputRequired(), Length(1, 64), Email()])
    new_password = PasswordField(_l('New password'),
                                 validators=[InputRequired(), EqualTo('new_password2', 'Passwords must match.')])
    new_password2 = PasswordField(_l('Confirm new password'), validators=[InputRequired()])
    submit = SubmitField(_l('Reset password'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(_('Unknown email address.'))


class CreatePasswordForm(FlaskForm):
    password = PasswordField(_l('Password'),
                             validators=[InputRequired(), EqualTo('password2', 'Passwords must match.')])
    password2 = PasswordField(_l('Confirm new password'), validators=[InputRequired()])
    submit = SubmitField(_l('Set password'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_l('Old password'), validators=[InputRequired()])
    new_password = PasswordField(_l('New password'),
                                 validators=[InputRequired(), EqualTo('new_password2', 'Passwords must match.')])
    new_password2 = PasswordField(_l('Confirm new password'), validators=[InputRequired()])
    submit = SubmitField(_l('Update password'))


class ChangeEmailForm(FlaskForm):
    email = EmailField(_l('New email'), validators=[InputRequired(), Length(1, 64), Email()])
    password = PasswordField(_l('Password'), validators=[InputRequired()])
    submit = SubmitField(_l('Update email'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(_('Email already registered.'))
