from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_rq import get_queue
from flask_babel import _

from app import db
from app.account.forms import ChangeEmailForm, ChangePasswordForm, CreatePasswordForm, LoginForm, RegistrationForm, \
    RequestResetPasswordForm, ResetPasswordForm
from app.email import send_email
from app.models import User, Role

account = Blueprint('account', __name__)


@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        # TODO | flash message if user is None
        try:
            user, user_role = db.session.query(User, Role).join(Role).filter(
                User.email == form.email_or_phone_number.data).first()
        except Exception as e:
            try:
                user, user_role = db.session.query(User, Role).join(Role).filter(
                    User.phone_number == form.email_or_phone_number.data).first()
            except Exception as e:
                flash(_('Please create a user'), 'form-check-email')
                return redirect(url_for('account.register'))

        if user is not None and user.password_hash is not None and \
            user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(_('You are now logged in. Welcome back!'), 'success')
            if user_role.index == 'admin':
                return redirect(request.args.get('next') or url_for('admin.index'))
            elif user_role.index == 'operator':
                return redirect(request.args.get('next') or url_for('operator.index'))
            elif user_role.index == 'teacher':
                return redirect(request.args.get('next') or url_for('teacher.index'))
            elif user_role.index == 'student':
                return redirect(request.args.get('next') or url_for('student.index'))
            else:
                return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash(_('Invalid email or password!'), 'form-error')
    return render_template('account/login.html', form=form)


@account.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user, and send them a confirmation email."""

    # TODO | disable these code bellow until Teachers and Students account feature available
    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     user = Student(
    #         first_name=form.first_name.data,
    #         last_name=form.last_name.data,
    #         email=form.email.data,
    #         password=form.password.data)
    #     db.session.add(user)
    #     db.session.commit()
    #     token = user.generate_confirmation_token()
    #     confirm_link = url_for('account.confirm', token=token, _external=True)
    #     get_queue().enqueue(
    #         send_email,
    #         recipient=user.email,
    #         subject='Confirm Your Account',
    #         template='account/email/confirm',
    #         user=user,
    #         confirm_link=confirm_link)
    #     flash(_('A confirmation link has been sent to your email'), 'warning')
    #     return redirect(url_for('account.login'))
    # return render_template('account/register.html', form=form)
    return redirect(url_for('account.login'))


@account.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@account.route('/manage/info', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None)


@account.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Respond to existing user's request to reset their password."""

    # TODO | disable these code bellow until Teachers and Students account feature available
    # if not current_user.is_anonymous:
    #     return redirect(url_for('main.index'))
    # form = RequestResetPasswordForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(email=form.email.data).first()
    #     if user:
    #         token = user.generate_password_reset_token()
    #         reset_link = url_for(
    #             'account.reset_password', token=token, _external=True)
    #         get_queue().enqueue(
    #             send_email,
    #             recipient=user.email,
    #             subject='Reset Your Password',
    #             template='account/email/reset_password',
    #             user=user,
    #             reset_link=reset_link,
    #             next=request.args.get('next'))
    #     flash(_('A password reset link has been sent to %(email)s.', email=user.form.email.data), 'warning')
    #     return redirect(url_for('account.login'))
    # return render_template('account/reset_password.html', form=form)
    return redirect(url_for('account.login'))


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash(_('Invalid email address!'), 'form-error')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash(_('Your password has been updated.'), 'form-success')
            return redirect(url_for('account.login'))
        else:
            flash(_('The password reset link is invalid or has expired.'), 'form-error')
            return redirect(url_for('main.index'))
    return render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash(_('Your password has been updated.'), 'form-success')
            return redirect(url_for('main.index'))
        else:
            flash(_('Original password is invalid!'), 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            change_email_link = url_for(
                'account.change_email', token=token, _external=True)
            get_queue().enqueue(
                send_email,
                recipient=new_email,
                subject='Confirm Your New Email',
                template='account/email/change_email',
                # current_user is a LocalProxy, we want the underlying user
                # object
                user=current_user._get_current_object(),
                change_email_link=change_email_link)
            flash(_('A confirmation link has been sent to %(new_email)s.', new_email=new_email), 'warning')
            return redirect(url_for('main.index'))
        else:
            flash(_('Invalid email or password!'), 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        flash(_('Your email address has been updated.'), 'success')
    else:
        flash(_('The confirmation link is invalid or has expired!'), 'error')
    return redirect(url_for('main.index'))


@account.route('/confirm-account')
@login_required
def confirm_request():
    """Respond to new user's request to confirm their account."""
    token = current_user.generate_confirmation_token()
    confirm_link = url_for('account.confirm', token=token, _external=True)
    get_queue().enqueue(
        send_email,
        recipient=current_user.email,
        subject='Confirm Your Account',
        template='account/email/confirm',
        # current_user is a LocalProxy, we want the underlying user object
        user=current_user._get_current_object(),
        confirm_link=confirm_link)
    flash(_('A new confirmation link has been sent to %(current_user_email)s.',
            current_user_email=current_user.email), 'warning')

    return redirect(url_for('main.index'))


@account.route('/confirm-account/<token>')
@login_required
def confirm(token):
    """Confirm new user's account with provided token."""
    if current_user.confirmed:
        return redirect(url_for(current_user.role.index + '.index'))
    if current_user.confirm_account(token):
        flash(_('Your account has been confirmed.'), 'success')
        return redirect(url_for(current_user.role.index + '.index'))
    else:
        flash(_('The confirmation link is invalid or has expired!'), 'error')
    return redirect(url_for('main.index'))


@account.route('/join-from-invite/<int:user_id>/<token>', methods=['GET', 'POST'])
def join_from_invite(user_id, token):
    """
    Confirm new user's account with provided token and prompt them to set
    a password.
    """
    if current_user is not None and current_user.is_authenticated:
        flash(_('You are already logged in.'), 'error')
        return redirect(url_for('main.index'))

    new_user = User.query.get(user_id)
    if new_user is None:
        return redirect(404)

    if new_user.password_hash is not None:
        flash(_('You have already joined.'), 'error')
        return redirect(url_for('main.index'))

    if new_user.confirm_account(token):
        form = CreatePasswordForm()
        if form.validate_on_submit():
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            flash(_('Your password has been set. After you log in, you can go to the "Your Account" '
                    'page to review your account information and settings.'), 'success')
            return redirect(url_for('account.login'))
        return render_template('account/join_invite.html', form=form)
    else:
        flash(_(
            'The confirmation link is invalid or has expired. '
            'Another invite email with a new link has been sent to you.'), 'error')
        token = new_user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user_id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=new_user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=new_user,
            invite_link=invite_link)
    return redirect(url_for('main.index'))


@account.before_app_request
def before_request():
    """Force user to confirm email before accessing login-required routes."""
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint[:8] != 'account.' \
        and request.endpoint != 'static':
        return redirect(url_for('account.unconfirmed'))


@account.route('/unconfirmed')
def unconfirmed():
    """Catch users with unconfirmed emails."""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for(current_user.role.index + '.index'))
    return render_template('account/unconfirmed.html')
