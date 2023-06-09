from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


@auth.route('/login',  methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.session.query(User).where(User.email == email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for("views.index"))
            else:
                flash("Incorrect password.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template('login.html', user=current_user)


@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        band = request.form.get("band")

        user = User.query.filter_by(email=email).first() # check if user exists
        if user:
            flash("Email already exists.", category="error")
        elif len(firstName) < 2:
            flash("First name must be longer than one character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 4:
            flash("Password must be longer than 4 digits.", category="error")
        else:
            new_user = User(email=email, first_name=firstName,
                            band=band, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for("views.index"))

    return render_template('sign-up.html', user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out!", category="success")
    return redirect(url_for("auth.login"))
