from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "User"

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean, default=False)

    # relationship
    progress = db.relationship("Progress", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class Task(db.Model):
    __tablename__ = "Task"

    id = db.Column(db.BigInteger, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text, nullable=True)
    answer = db.Column(db.Text, nullable=False)

    # relationship
    progress = db.relationship("Progress", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.id}>"


class Progress(db.Model):
    __tablename__ = "Progress"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("User.id"), nullable=False)
    task_id = db.Column(db.BigInteger, db.ForeignKey("Task.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    # relationships
    user = db.relationship("User", back_populates="progress")
    task = db.relationship("Task", back_populates="progress")

    def __repr__(self):
        return f"<Progress user={self.user_id} task={self.task_id} completed={self.completed}>"