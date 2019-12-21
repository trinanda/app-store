from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import StringField, SubmitField, FileField, FloatField
from wtforms import ValidationError, TextAreaField
from wtforms.validators import InputRequired, Length, required
from app.models import Product, Category


class ProductForm(FlaskForm):
    name = StringField(_l('Product name'), validators=[InputRequired(), Length(1, 100)])
    color = StringField(_l('Color'), validators=[Length(0, 100)])
    size = FloatField(_l('Size'), validators=[InputRequired()])
    barcode = StringField(_l('Barcode'), validators=[Length(1, 50)])
    image = FileField(_l('Course Image'))
    description = TextAreaField(_l('Description', validators=[Length(0, 100)]))
    category = QuerySelectField(_l('Category'), validators=[required('validators ')],
                                query_factory=lambda: Category.query.all())
    submit = SubmitField(_l('Add product'))

    def validate_name(form, field):
        if Product.query.filter_by(name=field.data).first():
            raise ValidationError(_('Product name already registered!'))
