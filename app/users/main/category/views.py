from flask import render_template, url_for, flash
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from flask_babel import _

from app import db
from app.models import Category
from app.users.main.category import category as bp
from app.users.main.category.forms import CategoryForm


@bp.route('/')
@bp.route('/categories')
def categories():
    categories = Category.query.all()
    for data in categories:
        print(data.created_at)
    return render_template('main/category/categories.html', categories=categories)


@bp.route('/add-category', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        try:
            db.session.commit()
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('category.add_category'))
        flash(_('Successfully added new category'), 'success')
        return redirect(url_for('category.categories'))
    return render_template('main/category/manipulate-category.html', form=form)


@bp.route('/delete_category/<int:category_id>')
def delete_category(category_id):
    """Delete a user's account."""
    category = Category.query.filter_by(id=category_id).first()
    if category is None:
        abort(404)
    db.session.delete(category)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'error')
        return redirect(url_for('category.categories', category_id=category_id))
    flash(_('successfully deleted %(category_name)s category', category_name=category.name), 'success')
    return redirect(url_for('category.categories'))


@bp.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    """Edit a category's information."""
    category = Category.query.filter_by(id=category_id).first()
    if category is None:
        abort(404)

    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        flash(_('Successfully edit category'), 'success')
        return redirect(url_for('category.categories'))
    return render_template('main/category/manipulate-category.html', category=category, form=form)
