from flask import Blueprint, request, redirect, render_template, url_for, flash, session, jsonify
from flask_login import login_user,logout_user, login_required, current_user
import smtplib
from datetime import timedelta
import random
from app import db
from app.models import User, Appointment
from passlib.hash import bcrypt
from email.message import EmailMessage
from email.mime.text import MIMEText

auth = Blueprint('auth', __name__)


def Appointment_mail(name, email, phone, gender, appType, appDate, message):

    username = 'bhattshubham247@gmail.com'
    password = 'tbjibaqtwregxvwn'

    SUBJECT = "Appointment Booked!"
    FROM = username
    TO = email
    TEXT = f'Dear {name}, \nYou have Booked an Appointment on our website. We will try to call you soon regarding your appointment and give you the timings.\n\nKindly, Do not reply on this mail.\n\nBest Regards,\nHMS Director'
    OWNER_TEXT = f'Dear Sir,\nPatient Name - {name}\nPatient Email - {email}\nPhone - {phone}\nGender - {gender}\nAppoint For - {appType}\nAppointment Date - {appDate}\nPatient Message - {message}\n\n Please Inform to {name} and give all the updates!\n\nRegards,\nBot HMS ORG'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO
    msg.set_content(TEXT)
    server.send_message(msg)


    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = TO
    msg['To'] = FROM
    msg.set_content(OWNER_TEXT)
    server.send_message(msg)
   
    server.quit()

def New_register(name, user_name, email):

    username = 'bhattshubham247@gmail.com'
    password = 'tbjibaqtwregxvwn'

    SUBJECT = f"ACCOUNT REGISTERED! | {user_name} | HMS ORG"
    FROM = username
    TO = email
    TEXT = f'Dear {name}, \nYou have registeres your account by this Username -> [{user_name}].\n\nKindly, Verify you account by clicking on the given link: http://127.0.0.1:5000/auth/login \n\nBest Regards,\nHMS Director'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    
    # TO USER
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO
    msg.set_content(TEXT)
    server.send_message(msg)
    server.quit()


@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST', 'GET'])
def login_post():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.verify(password, user.password):
            login_user(user)  # Log in the user
            session.permanent = True
            session['email'] = email
            return redirect(url_for('main.index'))
    
    flash('Invalid username or password')
    return redirect(url_for('auth.login'))

@auth.route('/profile')
def profile():
    if 'email' in session:
        return render_template('profile.html', name = current_user.name, profession = current_user.profession, bio = current_user.bio)
    else:
        return redirect(url_for('auth.login'))
    
@auth.route('/appointment')
@login_required
def book_an_appointment():
    return render_template('appointment.html')

@auth.route('/appointment', methods=['POST', 'GET'])
@login_required
def book_an_appointment_post():
     if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        appointmentType = request.form.get('appointmentType')
        other = request.form.get('other')
        booking_date = request.form.get('booking_date')
        message = request.form.get('message')

        print(name, email, booking_date, message)

        new_appointment = Appointment(name=name, email=email, phone=phone, gender=gender, appointmentType=appointmentType, other=other, booking_date = booking_date, message = message)

        db.session.add(new_appointment)
        db.session.commit()
        db.session.close()

        Appointment_mail(name, email, phone, gender, appointmentType, booking_date, message)

        return redirect(url_for('main.index'))

        # return render_template('appointment.html')  

@auth.route('/signup')
def register():
    return render_template('register.html')


@auth.route('/signup', methods=['POST', 'GET'])
def register_post():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username') 
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_pass = bcrypt.hash(password)

        user_email = User.query.filter_by(email=email).first()
        user_name = User.query.filter_by(username=username).first()
        if user_email and user_name:
            flash('This User already exists')
            return redirect(url_for('auth.register'))
        
        elif name == '' or email == '' or username == '' or password == '':
            flash('Fill all the Credentials')
            return redirect(url_for('auth.register'))
        
        else:
            new_user = User(username=username, name=name, email=email, password=hashed_pass)

            db.session.add(new_user)
            db.session.commit()
            db.session.close()

            New_register(name, username, email)

    return redirect(url_for('auth.login')) 


@auth.route('/forgotPassword')
def forgotPassword():
    return render_template('forget_password.html')

@auth.route('/forgotPassword', methods=['POST', 'GET'])
def forgot_password_post():
    if request.method == 'POST':
        forgData = request.json
        email = forgData['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect(url_for('auth.login'))

        else:    
            # update the user's password
            # msg = forgotten_mail(user.name, user.email)
            # print(msg)
            user.password = bcrypt.hash(forgData['password'])
            db.session.commit()
            db.session.close()
        
        return redirect(url_for('auth.login'))
   
    return redirect(url_for('auth.forgot_password'))

@auth.route('/passwordUpdated')
def passwordUpdated():
    return render_template('passwordUpdated.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    db.session.close()
    session.clear()
    return redirect(url_for('auth.login'))

