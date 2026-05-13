from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter(
            func.lower(User.username) == request.form["username"]
        ).first()
        print(user)
        if user:
            if check_password_hash(user.password, request.form["password"]):
                # success
                login_user(user)
                flash("Logged in as " + user.username, "success")
                return redirect(url_for('home'))
            else:
                # fail
                flash("Invalid username or password", "danger")
        else:
            flash("Invalid username or password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashedPass = generate_password_hash(request.form["password"])
        newUser = User(
            username = request.form["username"],
            password = hashedPass,
        )
        db.session.add(newUser)
        db.session.commit()
        flash("Account created, please log in", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('home'))