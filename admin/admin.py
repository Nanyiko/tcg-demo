from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
from models import db, User, Task, Progress, Class

admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")

@login_required
@admin_bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    tasks = Task.query.all()
    return render_template("admin/tasks.html", tasks=tasks, User=User, Progress=Progress)

@login_required
@admin_bp.route("/create_task", methods=["GET", "POST"])
def create_task():
    if request.method == "POST":
        newTask = Task(
            user_id = current_user.id,
            class_id = request.form["class-id"],
            title = request.form["title"],
            description = request.form["description"],
            hint = request.form["hint"],
        )
        db.session.add(newTask)
        db.session.commit()
        flash("Task created successfully", "success")
        return redirect(url_for("admin.tasks"))
    return render_template("admin/create_task.html", Class=Class)

@admin_bp.route("/save-classifier", methods=["POST"])
@login_required
def save_classifier():
    import json, os
    data = request.get_json()

    os.makedirs("static/classifier", exist_ok=True)
    with open("static/classifier/model.json", "w") as f:
        json.dump({k: v for k, v in data.items() if k not in ["class_name", "location", "lat", "lon"]}, f)

    new_class = Class(
        user_id=current_user.id,
        class_name=data["class_name"],
        location=data.get("location", False),
        lat=data.get("lat"),
        lon=data.get("lon")
    )
    db.session.add(new_class)
    db.session.commit()

    return jsonify({"status": "saved"})
