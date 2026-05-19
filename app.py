from flask import Flask, jsonify, render_template, request, Blueprint, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from auth.auth import auth_bp
from main.main import main_bp
from admin.admin import admin_bp
from models import db, User
import os

app = Flask(__name__)

folder_path = os.path.dirname(os.path.abspath(__file__))
app.config["SECRET_KEY"] = "INSERTACTUALSECRETKEYHERE"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{folder_path}/TCGDB.db"

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(admin_bp)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

@app.route("/")
def home():
    if current_user.is_authenticated:
        if bool(current_user.admin):
            return redirect(url_for("admin.tasks"))
        else:
            return redirect(url_for("main.tasks"))
    else:
        return redirect(url_for("welcome"))

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/scanner")
def scanner():
    return render_template("scanner.html")

def init_db():
    db_path = os.path.join(folder_path, "TCGDB.db")
    
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()

init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")