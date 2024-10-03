from flask import Flask, render_template, redirect, request, flash, url_for, session
from camera import Camera
from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
from forms import EnableForm, DisableForm

from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from __init__ import create_app, db, login_manager, bcrypt
from models import User
from forms import login_form, register_form
import logging

logging.basicConfig(
    filename="pi-camera.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)

logger = logging.getLogger(__name__)

app = create_app()
camera = Camera()
camera.arm()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        request_type = request.form.get("submit")
        if request_type == "ARM":
            camera.arm()
            return render_template("index.html", armed=camera.armed, form=DisableForm())
        elif request_type == "DISARM":
            camera.disarm()
            return render_template("index.html", armed=camera.armed, form=EnableForm())
    if camera.armed:
        form = DisableForm()
    else:
        form = EnableForm()
    return render_template("index.html", armed=camera.armed, form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if not user.is_admin:
                flash(f"{user.username} is not an admin.", "danger")
            elif check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template(
        "auth.html", form=form, text="Login", title="Login", btn_action="Login"
    )


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data

            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
                is_admin=False,
            )

            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"Integrity Constraint Violation!", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template(
        "auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account",
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
