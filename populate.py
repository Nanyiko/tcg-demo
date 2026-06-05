from app import app
from models import db, User, Class, Task, Progress
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
import random

with app.app_context():

    # ── Dummy users ──────────────────────────────────────────────
    dummy_users = []
    for i in range(1, 11):
        user = User(
            username=f"player{i}",
            password=generate_password_hash("password123"),
            admin=False
        )
        db.session.add(user)
        dummy_users.append(user)

    db.session.flush()  # get IDs without committing

    # ── Classes (must already exist, created by admin user id=1) ─
    pen_class   = Class.query.filter_by(class_name="pen").first()
    tv_class    = Class.query.filter_by(class_name="tv").first()
    remote_class = Class.query.filter_by(class_name="remote").first()

    if not all([pen_class, tv_class, remote_class]):
        print("ERROR: Could not find all 3 classes in the database.")
        print(f"  pen: {pen_class}")
        print(f"  tv: {tv_class}")
        print(f"  remote: {remote_class}")
        exit()

    # ── Tasks ────────────────────────────────────────────────────
    tasks_data = [
        {
            "class": pen_class,
            "title": "The Writer's Weapon",
            "description": (
                "I am mightier than the sword, or so they say. "
                "I leave a trail wherever I go, yet I carry no feet. "
                "I speak without a voice, sing without a tongue, "
                "and tell stories without ever opening my mouth. "
                "Students fear me at exam time, artists love me dearly, "
                "and offices would grind to a halt without me. "
                "I come in many colours, slim and tall, "
                "and I ask only for paper to give my all. "
                "What am I?"
            ),
            "hint": "You use it to write or draw. It fits in your hand and has ink inside."
        },
        {
            "class": tv_class,
            "title": "The Glowing Rectangle",
            "description": (
                "I hang on walls or stand on legs, a glowing rectangle in your home. "
                "I show you worlds you've never seen — jungles, oceans, distant stars. "
                "Heroes fight their battles on my face, villains plot and meet their fate. "
                "I can make you laugh, I can make you cry, "
                "I can teach you things or waste your time. "
                "Families gather around me after dinner, "
                "and children beg their parents for just five more minutes. "
                "I need a signal, a cable, or the air itself to speak. "
                "Turn me off and the room goes quiet. What am I?"
            ),
            "hint": "You watch shows and movies on it. It has a screen and usually sits in the living room."
        },
        {
            "class": remote_class,
            "title": "The Commander of Channels",
            "description": (
                "I am small but hold great power — with a press of my buttons "
                "I can silence giants and summon sound from across the room. "
                "I am always lost when you need me most, "
                "hiding under cushions, behind pillows, beneath the couch. "
                "I speak in a language of invisible light, "
                "whispering instructions to my loyal companion across the room. "
                "Batteries give me life; without them I am nothing. "
                "I have more buttons than you ever use, "
                "yet you know exactly which ones matter. What am I?"
            ),
            "hint": "You use it to control something else in the room. It runs on batteries and has lots of buttons."
        }
    ]

    tasks = []
    for t in tasks_data:
        task = Task(
            user_id=1,
            class_id=t["class"].id,
            title=t["title"],
            description=t["description"],
            hint=t["hint"],
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(task)
        tasks.append(task)

    db.session.flush()

    # ── Progress entries ─────────────────────────────────────────
    progress_entries = set()
    count = 0

    while count < 20:
        user   = random.choice(dummy_users)
        task   = random.choice(tasks)
        pair   = (user.id, task.id)

        if pair in progress_entries:
            continue

        progress_entries.add(pair)
        completed = random.choice([True, False])

        progress = Progress(
            user_id=user.id,
            task_id=task.id,
            completed=completed,
            completed_at=datetime.now(timezone.utc) if completed else None
        )
        db.session.add(progress)
        count += 1

    db.session.commit()
    print("Done! Created:")
    print(f"  10 dummy users (player1 - player10, password: password123)")
    print(f"  3 tasks (pen, tv, remote)")
    print(f"  20 progress entries")