from flask import render_template, url_for, flash, request
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from flask_babel import _

from app import db, photos
from app.models import Category, Product
from app.store.product import product as bp
from app.store.product.forms import ProductForm


@bp.route('/')
@bp.route('/products')
def products():
    products = Product.query.all()
    return render_template('store/product/products.html', products=products)


@bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product_name = form.name.data
        category = Category.query.filter_by(name=str(form.category.data)).first()
        try:
            filename = photos.save(request.files['image'], name="product/" + str(product_name) + "_product.")
        except Exception as e:
            flash(_('Please input correct image format'), 'error')
            return redirect(url_for('operator.add_course'))
        product = Product(
            name=product_name,
            category_id=category.id,
            description=form.description.data,
            color=form.color.data,
            image=filename,
            size=form.size.data,
            barcode=form.barcode.data,
        )
        db.session.add(product)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(str(e), 'error')
            return redirect(url_for('product.add_product'))
        flash(_('Successfully added new product'), 'success')
        return redirect(url_for('product.products'))
    return render_template('store/product/manipulate-product.html', form=form)


@bp.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    """Delete a user's account."""
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        abort(404)
    db.session.delete(product)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'error')
        return redirect(url_for('product.products'))
    flash(_('successfully deleted %(product_name)s product', product_name=product.name), 'success')
    return redirect(url_for('product.products'))


@bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit a product's information."""
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        abort(404)

    form = ProductForm(obj=product)
    if form.validate_on_submit():
        category = Category.query.filter_by(name=str(form.category.data)).first()

        product_name = form.name.data,
        product.name = product_name,
        product.color = form.color.data,
        product.size = form.size.data,
        product.barcode = form.barcode.data,
        product.category_id = category.id,
        product.description = form.description.data

        try:
            filename = photos.save(request.files['image'], name="product/" + str(product_name) + "_product.")
            product.image = filename
        except Exception as e:
            flash(_('Please input correct image format'), 'error')
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(_('Successfully edit product'), 'success')
            return redirect(url_for('product.edit_product', product_id=product_id))
        flash(_('Successfully edit product'), 'success')
        return redirect(url_for('product.products'))
    return render_template('store/product/manipulate-product.html', product=product, form=form)
