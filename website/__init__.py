from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# python_anywhere_pass = "<MySQL>01"
# DB_PASS = "calpass"
# DB_STRING = "postgresql://calendar:calpass@34.92.116.155/calendar"
# DB_STRING = "postgresql://calendar:calpass@/calendar?host=/cloudsql/gflask-382913:asia-east2:calendar" - google string
db = SQLAlchemy()  # need to construct outside of def because of import
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "yoursecretkey"
    #app.config['SQLALCHEMY_DATABASE_URI'] = DB_STRING
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
    #   for pythonanywhere mysql connection string
    #  app.config[
    #     'SQLALCHEMY_DATABASE_URI'] = 'mysql://Pickelstif:<MySQL>01@Pickelstif.mysql.pythonanywhere-services.com/Pickelstif$calendar'
    db.init_app(app)  # need to do this because db was constructed without an app

    from .models import User, Availability
    with app.app_context():
        db.create_all()

    from .auth import auth
    from .views import views

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(views, url_prefix="/")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user = User.query.get(int(id))
        user.bandmates = {}
        query = User.query.filter_by(band=user.band).all()
        for name in query:
            user.bandmates[name.email] = name.first_name

        # user.bandmates['email'] = [name.email for name in User.query.filter_by(band=user.band) if name.email != user.email]
        # user.bandmates['name'] = [name.first_name for name in User.query.filter_by(band=user.band) if name.first_name != user.first_name]
        # added a custom parameter to the User model - must do it here to be persistent
        return user

    return app

