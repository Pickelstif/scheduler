from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Bands, User_Band_Junction
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

def add_membership(band, user):
    return User_Band_Junction(band_name=band, member_id=user)

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
        band_name = request.form.get("band")

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
            band = Bands.query.filter_by(band_name=band_name).first()
            if not band:
                band = Bands(band_name=band_name)
            db.session.add(band)
            db.session.commit()
            band = Bands.query.filter_by(band_name=band_name).first()

            new_user = User(email=email, first_name=firstName,
                            password=generate_password_hash(password1, method="sha256"), active_band=band.id) #don't think it'll work because id hasn't been created

            db.session.add(new_user)
            db.session.commit()
            new_user = User.query.filter_by(email=email).first()
            new_member = add_membership(band.band_name, new_user.id)

            db.session.add(new_member)
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
