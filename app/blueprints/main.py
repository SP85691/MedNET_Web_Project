from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user, login_remembered
from email.message import EmailMessage
import smtplib
from app.models import User, Contact_Us
from app import db

main = Blueprint('main', __name__) 

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about_Sec():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/get_in_touch', methods=['POST', 'GET'])
def get_in_touch():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

            contact_upt = Contact_Us(name=name, email=email, message=message)

            db.session.add(contact_upt)
            db.session.commit()
            db.session.close()

        return redirect(url_for('main.index')) 

def get_in_touch(name, email, message):

    username = 'bhattshubham247@gmail.com'
    password = 'tbjibaqtwregxvwn'

    SUBJECT = "Get in Touch :)"
    FROM = username
    TO = email
    TEXT_USER = f'Dear {name}, \nThank you for indulging with us. We will try to resolve your query and let you know as soon as possible.\n\nKindly, Do not Reply on this mail.\n\nBest Regards,\nShubham Bhatt'
    TEXT_OWNER = f"Dear Sir, \n{name} has sent you a mail. he is getting some query. here is the query of {name}\n\n{name}'s Query -> {message}.\n\nKindly, Reply him/her as soon as possible.\n\nRegards,\nBot HMS"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    
    # To User
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO
    msg.set_content(TEXT_USER)
    server.send_message(msg)

    # To Owner
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = TO
    msg['To'] = FROM
    msg.set_content(TEXT_OWNER)
    server.send_message(msg)

    server.quit()
