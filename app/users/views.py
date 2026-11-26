from flask import request, redirect, url_for, render_template, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from . import users_bp
from .forms import RegistrationForm, LoginForm
from .models import User

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

@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.hash_password(form.password.data)  # хешування пароля перед збереженням
        db.session.add(user)
        db.session.commit()
        flash(f"Обліковий запис {form.username.data} успішно створено! Тепер ви можете увійти.", "success")
        return redirect(url_for("users.login"))
    return render_template("users/register.html", form=form, title="Реєстрація")


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Вітаю, {user.username}! Вхід успішний.", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("users.account"))
        flash("Невірний email або пароль. Спробуйте ще раз.", "danger")
    return render_template("users/login.html", form=form, title="Вхід")


@users_bp.route("/account")
@login_required
def account():
    # current_user надає доступ до даних автентифікованого користувача
    return render_template("users/account.html", user=current_user)


@users_bp.route("/users")
@login_required
def users_list():
    users = db.session.scalars(db.select(User).order_by(User.id)).all()
    return render_template("users/users.html", users=users)


@users_bp.route("/profile")
@login_required
def profile():
    return render_template("users/profile.html", username=current_user.username)


@users_bp.route("/logout")
def logout():
    logout_user()
    flash("Ви успішно вийшли з системи.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/add_cookie", methods=["POST"])
def add_cookie():
    if not current_user.is_authenticated:
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
    if not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(key)
    flash(f"Кукі '{key}' успішно видалено!", "info")
    return response


@users_bp.route("/delete_all_cookies")
def delete_all_cookies():
    if not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))

    for key in request.cookies:
        if key != "session":
            response.delete_cookie(key)

    flash("Всі кукі успішно видалено!", "info")
    return response


@users_bp.route("/theme/<color>")
def change_theme(color):
    if not current_user.is_authenticated:
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie("theme", color, max_age=30 * 24 * 60 * 60)
    return response