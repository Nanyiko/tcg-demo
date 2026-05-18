from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean, default=False)

    # relationships
    tasks = db.relationship("Task", back_populates="creator", cascade="all, delete-orphan")
    progress = db.relationship("Progress", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Task(db.Model):
    __tablename__ = "Task"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("User.id"), nullable=False)

    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text, nullable=True)
    answer = db.Column(db.Text, nullable=False)

    # relationships
    creator = db.relationship("User", back_populates="tasks")
    progress = db.relationship("Progress", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.title}>"


class Progress(db.Model):
    __tablename__ = "Progress"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("User.id"), nullable=False)
    task_id = db.Column(db.BigInteger, db.ForeignKey("Task.id"), nullable=False)

    completed = db.Column(db.Boolean, default=False)

    # relationships
    user = db.relationship("User", back_populates="progress")
    task = db.relationship("Task", back_populates="progress")

    __table_args__ = (
        db.UniqueConstraint("user_id", "task_id", name="unique_user_task"),
    )

    def __repr__(self):
        return f"<Progress user={self.user_id} task={self.task_id} completed={self.completed}>"