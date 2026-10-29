from flask import render_template
from . import app

@app.route('/')
def resume():
    return render_template('resume.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/homepage')
def home():
    """View for the Home page of your website."""
    return render_template("homepage.html")