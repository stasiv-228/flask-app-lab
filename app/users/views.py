from flask import request, redirect, url_for, render_template, session, flash, make_response
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


@users_bp.route("/add_cookie", methods=["POST"])
def add_cookie():
    if "username" not in session:
        return redirect(url_for("users.login"))

    key = request.form.get("cookie_key")
    value = request.form.get("cookie_value")
    exp_days = request.form.get("cookie_exp", type=int, default=1)

    response = make_response(redirect(url_for("users.profile")))

    max_age = exp_days * 24 * 60 * 60
    response.set_cookie(key, value, max_age=max_age)

    flash(f"Кукі '{key}' успішно додано!", "success")
    return response


@users_bp.route("/delete_cookie/<key>")
def delete_cookie(key):
    if "username" not in session:
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(key)
    flash(f"Кукі '{key}' успішно видалено!", "info")
    return response


@users_bp.route("/delete_all_cookies")
def delete_all_cookies():
    if "username" not in session:
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))

    for key in request.cookies:
        if key != "session":
            response.delete_cookie(key)

    flash("Всі кукі успішно видалено!", "info")
    return response