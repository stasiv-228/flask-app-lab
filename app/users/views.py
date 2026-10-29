from flask import request, redirect, url_for, render_template, session, flash
from . import users_bp

@users_bp.route("/hi/<string:name>")  # /hi/ivan?age=45
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template("users/hi.html", name=name, age=age)

@users_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    print(to_url)
    return redirect(to_url)

VALID_USERNAME = "Student"
VALID_PASSWORD = "password123"

@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("users.profile"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session["username"] = username
            flash("Ви успішно увійшли в систему!", "success")
            return redirect(url_for("users.profile"))
        else:
            flash("Невірний логін або пароль. Спробуйте ще раз.", "error")

    return render_template("users/login.html")

@users_bp.route("/profile")
def profile():
    if "username" not in session:
        flash("Будь ласка, увійдіть у систему для перегляду профілю.", "warning")
        return redirect(url_for("users.login"))

    username = session["username"]
    return render_template("users/profile.html", username=username)

@users_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Ви успішно вийшли з системи.", "info")
    return redirect(url_for("users.login"))