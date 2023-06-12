from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from datetime import datetime
from calendar import monthcalendar
from . import db
from .models import Availability, User

views = Blueprint('views', __name__)


def availabilities(month, user=current_user):
    days = [int(day[0])
            for day in db.session.query(Availability.day).where(Availability.month == str(month),
                                                                Availability.user_id == str(user.id))]
    return days


def get_date(input=datetime.now().strftime("%Y-%m")):
    try:
        year, month = input.split("-")
        output = [int(year), int(month)]
    except:
        year, month = datetime.now().strftime("%Y-%m").split("-")
        output = [int(year), int(month)]
    return output


@views.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
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


@views.route('/available', methods=['GET', 'POST'])
@login_required
def available(): # common days tab
    form_date = get_date(request.form.get('mdate', datetime.now().strftime("%Y-%m")))
    cal = monthcalendar(form_date[0], form_date[1])
    user_ids = [user.id for user in User.query.filter_by(band=current_user.band).all()]  # important SQLAlchemy usage
    all_user_days = []
    for ids in user_ids:
        user_days = [int(x.day) for x in Availability.query.filter_by(user_id=ids, month=str(form_date[1])).all()]
        if user_days:
            all_user_days.append(user_days)
    try:
        common_days = list(set.intersection(*map(set, all_user_days)))
    except TypeError:
        common_days = []
    avail_days = availabilities(form_date[1])
    return render_template('available.html', cal=cal, month=form_date[1], year=form_date[0],
                           availabilities=avail_days, common_days=common_days, user=current_user)

@views.route('/bandmates', methods=['GET', 'POST'])
@login_required
def bandmates():
    form_date = get_date(request.args.get('mdate', datetime.now().strftime("%Y-%m")))
    cal = monthcalendar(form_date[0], form_date[1])
    bandmates_availabilities = {current_user.bandmates[bandmate]:availabilities(form_date[1], user=User.query.filter_by(email=bandmate).first()) for bandmate in current_user.bandmates}
    return render_template('bandmates.html', cal=cal, month=form_date[1], year=form_date[0], user=current_user, bandmates_availabilities=bandmates_availabilities)