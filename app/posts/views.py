from flask import render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm

from app import db
from . import post_bp
from .forms import PostForm
from .models import Post


@post_bp.route("/")
def all_posts():
    """Список усіх активних постів за датою публікації (спадання)"""
    stmt = db.select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc())
    posts = db.session.scalars(stmt).all()
    return render_template("posts.html", posts=posts)


@post_bp.route("/<int:id>")
def detail_post(id):
    """Перегляд окремого поста"""
    post = db.get_or_404(Post, id)
    return render_template("detail_post.html", post=post)


@post_bp.route("/create", methods=["GET", "POST"])
def add_post():
    """Створення нового поста"""
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            is_active=form.is_active.data,
            posted=form.publish_date.data,
            category=form.category.data,
            author=session.get("username", "Anonymous"),  # автор — користувач із сесії
        )
        db.session.add(new_post)
        db.session.commit()
        flash(f"Пост «{new_post.title}» успішно додано!", "success")
        return redirect(url_for(".all_posts"))
    elif request.method == "POST":
        flash("Введіть коректні дані у форму!", "danger")

    return render_template("add_post.html", form=form, title="Створити пост")


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    """Редагування поста"""
    post = db.get_or_404(Post, id)   # якщо об'єкт не знайдено — помилка 404
    form = PostForm(obj=post)        # заповнення форми даними поста
    if request.method == "GET":
        form.publish_date.data = post.posted  # назви полів у формі та моделі різні

    if form.validate_on_submit():
        form.populate_obj(post)               # оновлення об'єкта post з форми
        post.posted = form.publish_date.data
        db.session.commit()
        flash(f"Пост «{post.title}» успішно оновлено!", "success")
        return redirect(url_for(".detail_post", id=post.id))
    elif request.method == "POST":
        flash("Введіть коректні дані у форму!", "danger")

    return render_template("add_post.html", form=form, title="Редагувати пост", post=post)


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    """GET — сторінка підтвердження, POST — видалення поста"""
    post = db.get_or_404(Post, id)
    form = FlaskForm()  # порожня форма лише для CSRF-захисту

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash(f"Пост «{post.title}» успішно видалено.", "danger")
        return redirect(url_for(".all_posts"))

    return render_template("delete_confirm.html", post=post, form=form)
