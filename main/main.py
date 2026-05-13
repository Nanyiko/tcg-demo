from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from models import db, User, Task, Progress

main_bp = Blueprint("main", __name__, url_prefix="/main", template_folder="templates")

@main_bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    return render_template("main/tasks.html")