import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from datetime import date, timedelta

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "minha_chave_super_secreta_12345"
Session(app)

db = SQL("sqlite:///habits.db")

# rota principal
@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    habits = db.execute("SELECT * FROM habits WHERE user_id = ?", user_id)
    today = date.today().isoformat()

    for habit in habits:
        logs = db.execute(
            "SELECT * FROM habit_logs WHERE habit_id = ? AND completed_at = ?",
            habit["id"], today
        )
        habit["is_completed"] = len(logs) > 0

        # verificar streak
        habit["streak"] = calculate_streak(habit["id"])

    return render_template("index.html", habits=habits)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Username is required", 400)
        elif not password:
            return apology("Password is required", 400)
        elif not confirmation:
            return apology("You must confirm your password", 400)
        elif password != confirmation:
            return apology("Passwords do not match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Checando por duplicatas
        if len(rows) != 0:
            return apology("Username already exists", 400)

        # Registrando novo usuário válido
        hash_password = generate_password_hash(password)
        user_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)

        # Criar nova sessão para o usuário (o CS50 db.execute no INSERT já retorna o ID do novo registro!)
        session["user_id"] = user_id

        # Redirecionar para a home
        return redirect("/")

    else:
        return render_template("register.html")

#login
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("Username is required", 400)

        elif not password:
            return apology("Password is required", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Verificar se o nome existe e a senha está correta
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password", 403)

        # Lembrar qual usuário logou
        session["user_id"] = rows[0]["id"]

        # Redirecionar para a home
        return redirect("/")

    else:
        return render_template("login.html")

#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#adicionar habito
@app.route("/add", methods = ["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        title = request.form.get("title")
        frequency = request.form.get("frequency") or "daily"

        if not title:
            return apology("Habit title is required", 400)

        user_id = session["user_id"]

        db.execute("INSERT INTO habits (user_id, title, frequency) VALUES (?, ?, ?)",user_id, title, frequency)

        return redirect("/")
    else:
        return render_template("add.html")

# deletar habito
@app.route("/delete", methods=["POST"])
@login_required
def delete():
    habit_id = request.form.get("id")
    user_id = session["user_id"]

    if habit_id:
        db.execute("DELETE FROM habits WHERE id = ? AND user_id = ?", habit_id, user_id)

    return redirect("/")

#completar um hábito
@app.route("/complete", methods=["POST"])
@login_required
def complete():
    habit_id = request.form.get("habit_id")
    user_id = session["user_id"]

    if habit_id:
        today = date.today().isoformat()

        # 1. Busca se já existe um log para este hábito hoje
        existing_log = db.execute(
            "SELECT * FROM habit_logs WHERE habit_id = ? AND user_id = ? AND completed_at = ?",
            habit_id, user_id, today
        )

        # 2. Se NÃO existir (lista vazia), faz o registro
        if not existing_log:
            db.execute(
                "INSERT INTO habit_logs (habit_id, user_id, completed_at) VALUES (?, ?, ?)",
                habit_id, user_id, today
            )

    return redirect("/")

def calculate_streak(habit_id):
    #listar os registro do habito
    register = db.execute("SELECT DISTINCT completed_at FROM habit_logs WHERE habit_id = ? ORDER BY completed_at DESC", habit_id)
    #verificar se os registros estao vazios
    if not register:
        return 0
    #armazenas data do registro mais recente
    last_date = date.fromisoformat(register[0]["completed_at"])
    #definir valores para hoje e ontem
    today = date.today()
    yesterday = today - timedelta(days=1)
    streak = 0
    check_date = last_date

    if last_date != today and last_date != yesterday:
        return streak

    for log in register:
        current_date = date.fromisoformat(log["completed_at"])
        if current_date == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

def apology(message, code=400):
    flash(message, "danger")

    return redirect(request.referrer or "/")
