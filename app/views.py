import logging
from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import ContactForm

main_bp = Blueprint('main', __name__)

logging.basicConfig(
    filename='contact.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

@main_bp.route('/')
def resume():
    return render_template('resume.html')

@main_bp.route('/contacts', methods=['GET', 'POST'])
def contacts():
    form = ContactForm()

    if form.validate_on_submit():
        logging.info(
            f"Нове повідомлення | Name: {form.name.data} | "
            f"Email: {form.email.data} | Phone: {form.phone.data} | "
            f"Subject: {form.subject.data} | Message: {form.message.data}"
        )
        flash(f"Дякуємо, {form.name.data}! Ваші дані успішно надіслано та записано в лог.", "success")
        return redirect(url_for('main.contacts'))

    if form.is_submitted() and not form.validate():
        flash("Помилка валідації! Перевірте правильність заповнення полів.", "danger")

    return render_template('contacts.html', form=form)

@main_bp.route('/homepage')
def home():
    """View for the Home page of your website."""
    return render_template("homepage.html")