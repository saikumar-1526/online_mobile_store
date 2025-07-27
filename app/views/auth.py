from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.security import check_password_hash, generate_password_hash
from ..models.app_models import User, db, Cart
from functools import wraps
from flask_login import current_user, login_user, logout_user, login_required, current_user
from ..utils import email_util
import uuid

auth_bp = Blueprint('auth', __name__)

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                # Redirect to login if user is not logged in
                print("ROle", required_role)
                return redirect(url_for('auth.login', role=required_role))

            if current_user.role != required_role:
                # Flash a message and redirect if user does not have the required role
                flash(f"You do not have permission to access this page. {required_role.capitalize()} role required.")
                return redirect(url_for('auth.logout'))  # Or return a 403 response if needed
            return func(*args, **kwargs)

        return decorated_view

    return decorator

# General registration route
@auth_bp.route('/register/<role>/', methods=['GET', 'POST'])
def register(role):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        if (role == "customer"):
            verifier = f"{uuid.uuid4()}_{uuid.uuid4()}"
            # Create a new user instance
            flash("Verify your account to login")
            new_user = User(username=username, password=hashed_password, role=role, first_name=firstname, last_name=lastname, verifier=verifier)

            email_util.verify_email(username, firstname + lastname, f"Account Verification for {firstname}", verifier, f'{"/".join(request.base_url.split("/")[:-3])}/')
        else:
            new_user = User(username=username, password=hashed_password, role=role, first_name=firstname,
                        last_name=lastname)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login', role=role))
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"}), 500

    return render_template('auth/register.html', role=role)


# General login route
@auth_bp.route('/login/<role>/', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.index'))
            elif user.role == 'customer':
                return redirect(url_for('public.index'))
        else:
            flash("Incorrect username or password.", "failure")
            return render_template('auth/login.html',role=role), 401

    return render_template('auth/login.html',role=role)

# General login route
@auth_bp.route('/login_redirect/', methods=['GET', 'POST'])
def login_redirect():
    next_page = request.args.get('next')
    if('/admin/' in next_page):
        return redirect(url_for('auth.login', role='admin'))
    return redirect(url_for('auth.login', role='customer'))

# General login route
@auth_bp.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    role = current_user.role
    logout_user()
    if role == 'admin':
        return redirect(url_for('auth.login', role = 'admin'))
    return redirect(url_for('auth.login', role = 'customer'))

@auth_bp.route('/verify_user/', methods=['GET'])
def verify_user():
    verifier = request.args.get("s")
    user = User.query.filter_by(verifier=verifier).first()
    if(user):
        user.is_verified = True
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('public.index'))
    flash("Unable to verify user.")
    return redirect(url_for('auth.login', role = 'customer'))