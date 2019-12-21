from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms.fields import StringField, SubmitField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Length
from app.models import Category


class CategoryForm(FlaskForm):
    name = StringField(_l('Category name'), validators=[InputRequired(), Length(1, 100)])
    submit = SubmitField(_l('Add category'))

    def validate_name(form, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError(_('Category name already registered!'))
