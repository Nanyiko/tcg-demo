from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from models import db, User, Task, Progress

admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")

@login_required
@admin_bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    return render_template("admin/tasks.html")

@login_required
@admin_bp.route("/create_task", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        newTask = Task(
            user_id = current_user.id,
            title = request.form["title"],
            description = request.form["description"],
            hint = request.form["hint"],
            answer = request.form["answer"],
        )
        db.session.add(newTask)
        db.session.commit()
        flash("Account created, please log in", "success")
        return redirect(url_for("admin.tasks"))
    return render_template("admin/create_task.html")