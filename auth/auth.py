from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        newUser = User(
            username = request.form["username"],
            password = request.form["password"],
        )
        db.session.add(newUser)
        db.session.commit()
        flash("Account created, please log in", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")
