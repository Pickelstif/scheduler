from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime
from calendar import monthcalendar
from . import db
from .models import Availability, User, Bands, User_Band_Junction

views = Blueprint('views', __name__)


def availabilities(month, user=current_user):
    days = [int(day[0])
            for day in db.session.query(Availability.day).where(Availability.month == str(month),
                                                                Availability.user_id == str(user.id))]
    return days


def get_date(form_date=datetime.now().strftime("%Y-%m")):
    try:
        year, month = form_date.split("-")
        output = [int(year), int(month)]
    except:
        year, month = datetime.now().strftime("%Y-%m").split("-")
        if datetime.now().day > 14:
            output = [int(year), int(month) + 1]
        else:
            output = [int(year), int(month)]
    return output


def update_band(band_name):
    band = Bands.query.filter_by(band_name=band_name).first().id
    if band:
        current_user.active_band = band
    else:
        current_user.active_band = 1
    db.session.commit()

def remove_member(band_name):
    band = Bands.query.filter_by(band_name=band_name).first()
    if band:
        membership = User_Band_Junction.query.filter_by(band_name=band_name, member_id=current_user.id).first()
        if membership:
            db.session.delete(membership)
            db.session.commit()
        #check if any member remains for the band. Delete the band if no one exists
        any_member = User_Band_Junction.query.filter_by(band_name=band_name).first()
        if not any_member:
            db.session.delete(band)
            db.session.commit()






def add_band(band_name):
    band = Bands.query.filter_by(band_name=band_name).first()
    if band:
        membership = User_Band_Junction.query.filter_by(band_name=band_name, member_id=current_user.id).first()
        if membership:
            return flash("You're already a member.", category="error")
    else:
        new_band = Bands(band_name=band_name)
        db.session.add(new_band)
        db.session.commit()

    new_member = User_Band_Junction(band_name=band_name, member_id=current_user.id)
    db.session.add(new_member)
    db.session.commit()


@views.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        print(request.form)
        date_as_string = f'{request.form.get("year")}-{request.form.get("month")}'
        form_date = get_date(date_as_string)
        # print(Availability().query.filter_by(month=request.form.get("month")).all()) --- a way to query a database
        active_month_db = db.session.query(Availability).where(Availability.month == str(form_date[1]),
                                                               Availability.user_id == str(current_user.id))
        for availability in active_month_db:
            db.session.delete(availability)

        info = [date for date in request.form.getlist("dates") if date]
        for date in info:
            new_availability = Availability(day=date, month=form_date[1], user_id=current_user.id)
            db.session.add(new_availability)
        db.session.commit()
        flash("Available days successfully saved!", category="success")
        return redirect(url_for('views.index', year=form_date[0], month=form_date[1], user=current_user))
    else:
        if request.args.get("mdate"):
            date_as_string = request.args.get("mdate")
        else:
            date_as_string = f'{request.args.get("year")}-{request.args.get("month")}'
        form_date = get_date(date_as_string)
        cal = monthcalendar(form_date[0], form_date[1])  # gives week view with zero as days that don't exist that mont
        avail_days = availabilities(form_date[1])
        return render_template('index.html', cal=cal, month=form_date[1], year=form_date[0],
                               availabilities=avail_days, user=current_user)


@views.route('/common', methods=['GET', 'POST'])
@login_required
def common():  # common days tab
    form_date = get_date(request.form.get('mdate'))
    cal = monthcalendar(form_date[0], form_date[1])
    # user_ids = [user.id for user in User.query.filter_by(band=current_user.band).all()]  # important SQLAlchemy usage
    all_user_days = []
    for ids in current_user.bandmates:
        user_days = [int(x.day) for x in Availability.query.filter_by(user_id=ids, month=str(form_date[1])).all()]
        if user_days:
            all_user_days.append(user_days)
    try:
        common_days = list(set.intersection(*map(set, all_user_days)))
    except TypeError:
        common_days = []
    avail_days = availabilities(form_date[1])
    return render_template('common.html', cal=cal, month=form_date[1], year=form_date[0],
                           availabilities=avail_days, common_days=common_days, user=current_user)


@views.route('/bandmates', methods=['GET', 'POST'])
@login_required
def bandmates():
    form_date = get_date(request.args.get('mdate'))
    cal = monthcalendar(form_date[0], form_date[1])
    bandmates_availabilities = {}
    for bandmate_id in current_user.bandmates:
        bandmate = User.query.filter_by(id=bandmate_id).first()
        bandmates_availabilities[bandmate.first_name] = availabilities(form_date[1], user=bandmate)
    return render_template('bandmates.html', cal=cal, month=form_date[1], year=form_date[0], user=current_user,
                           bandmates_availabilities=bandmates_availabilities)


@views.route('/update-band-f', methods=['POST'])
@login_required
def update_band_f():
    if request.method == "POST":
        band_name = request.form.get("band")
        update_band(band_name)
        return redirect(url_for("views.common"))


@views.route('/add-new-band', methods=['GET', 'POST'])
@login_required
def add_new_band():
    if request.method == "POST":
        band_name = request.form.get("band_name")
        add_band(band_name)
        update_band(band_name)
        return redirect(url_for('views.common'))

    return render_template('add-new-band.html', user=current_user)

@views.route('/delete-band', methods=['GET', 'POST'])
@login_required
def delete_band():
    if request.method == "POST":
        band_name = request.form.get("band_name")
        print(band_name)
        remove_member(band_name)

        first_membership = User_Band_Junction.query.filter_by(member_id=current_user.id).first().band_name
        current_user.active_band = Bands.query.filter_by(band_name=first_membership).first().id
        db.session.commit()
        return redirect(url_for('views.common'))

    return render_template('delete-band.html', user=current_user)