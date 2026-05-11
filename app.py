from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import LoginManager, current_user, login_required
from auth.auth import auth_bp
from models import db, User
import os

app = Flask(__name__)

folder_path = os.path.dirname(os.path.abspath(__file__))
app.config["SECRET_KEY"] = "INSERTACTUALSECRETKEYHERE"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{folder_path}/TCGDB.db"

app.register_blueprint(auth_bp)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scanner")
def scanner():
    return render_template("scanner.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
