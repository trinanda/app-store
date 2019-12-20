from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_rq import get_queue
from flask_babel import _

from app.users.admin.forms import ChangeAccountTypeForm, ChangeUserEmailForm, InviteUserForm, EditUserForm, NewUserForm
from app import db
from app.decorators import admin_required
from app.email import send_email
from app.models import EditableHTML, Role, User, Teacher, Operator, Student

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    users = db.session.query(User.id, User, Role).join(Role).order_by(User.updated_at.desc()).all()
    return render_template('admin/index.html', users=users)


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        if form.role.data.__dict__['name'] == 'Administrator':
            user = User(
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data,
                confirmed=True
            )
            db.session.add(user)
            db.session.commit()
            flash(_('User %(user_full_name)s successfully created.', user_full_name=user.full_name), 'success')

        elif form.role.data.__dict__['name'] == 'Operator':
            operator = Operator(
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data,
                confirmed=True
            )
            db.session.add(operator)
            db.session.commit()
            flash(_('Operator %(operator_full_name)s successfully created.', operator_full_name=operator.full_name),
                  'success')

        elif form.role.data.__dict__['name'] == 'Teacher':
            teacher = Teacher(
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data,
                confirmed=True
            )
            db.session.add(teacher)
            db.session.commit()
            flash(_('Teacher %(teacher_full_name)s successfully created.', teacher_full_name=teacher.full_name),
                  'success')

        elif form.role.data.__dict__['name'] == 'Student':
            student = Student(
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data,
                confirmed=True
            )
            db.session.add(student)
            db.session.commit()
            flash(_('Student %(student_full_name)s successfully created.', student_full_name=student.full_name),
                  'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/manipulate-user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link)
        flash(_('User %(user_full_name)s successfully invited.', user_full_name=user.full_name), 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/manipulate-user.html', form=form)


@admin.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)

    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.role = form.role.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        validate_user_data = User.query.filter(~User.phone_number.in_([user.phone_number])).all()
        all_user_email = []

        for data in validate_user_data:
            all_user_email.append(data.email)

        if form.email.data in all_user_email:
            flash(_('Duplicate email with the other users, please input different email!'), 'error')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        user.email = form.email.data

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return redirect(url_for('admin.edit_user', user_id=user_id))
        flash(_('Successfully edited user %(user_full_name)s.', user_full_name=user.full_name), 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/manipulate-user.html', form=form, user=user)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash(_('Email for user %(user_full_name)s successfully changed to %(user_email)s.',
                user_full_name=user.full_name, user_email=user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash(_('You cannot change the type of your own account. Please ask another administrator to do this.'),
              'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash(
            _('Role for user %(user_full_name)s successfully changed to %(user_role)s.', user_full_name=user.full_name,
              user_role=user.role), 'form-success')

    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash(_('You cannot delete your own account. Please ask another administrator to do this.'), 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash(_('Successfully deleted user %(user_full_name)s.', user_full_name=user.full_name), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""
    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200
