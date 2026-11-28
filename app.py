
import os
import logging
import sys
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, abort, render_template_string, session
from werkzeug.security import check_password_hash

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s", stream=sys.stdout)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.secret_key = os.environ.get("APP_SECRET", "local-development-only-change-me")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")


def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not ADMIN_PASSWORD_HASH:
            error = "Login is not configured. Contact the administrator."
        elif username == ADMIN_USERNAME and check_password_hash(
            ADMIN_PASSWORD_HASH, password
        ):
            session.clear()
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    conn = get_db()
    try:
        tasks = conn.execute("SELECT * FROM tasks").fetchall()
    finally:
        conn.close()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title", "").strip()

    if not title:
        abort(400, description="Task title cannot be empty.")

    conn = get_db()
    try:
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("home"))


@app.route("/update/<int:task_id>", methods=["POST"])
@login_required
def update(task_id):
    title = request.form.get("title", "").strip()

    if not title:
        abort(400, description="Task title cannot be empty.")

    conn = get_db()
    try:
        result = conn.execute(
            "UPDATE tasks SET title = ? WHERE id = ?",
            (title, task_id)
        )
        conn.commit()

        if result.rowcount == 0:
            abort(404)
    finally:
        conn.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>")
@login_required
def delete(task_id):
    conn = get_db()
    try:
        result = conn.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )
        conn.commit()

        if result.rowcount == 0:
            abort(404)
    finally:
        conn.close()

    return redirect(url_for("home"))


@app.route("/api/tasks")
@login_required
def api_tasks():
    conn = get_db()
    try:
        tasks = conn.execute("SELECT * FROM tasks").fetchall()
    finally:
        conn.close()

    return {"tasks": [dict(task) for task in tasks]}


@app.errorhandler(400)
def bad_request(error):
    return render_template_string(
        "<h1>400 - Bad Request</h1><p>{{ message }}</p>",
        message=error.description
    ), 400


@app.errorhandler(404)
def not_found(error):
    return "<h1>404 - Page or task not found</h1>", 404


@app.errorhandler(500)
def server_error(error):
    app.logger.exception("An unexpected server error occurred")
    return "<h1>500 - Internal Server Error</h1>", 500


if __name__ == "__main__":
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    app.run(host="0.0.0.0", port=5000, debug=False)
