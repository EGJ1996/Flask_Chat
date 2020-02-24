from flask import Blueprint, render_template,session, Response, jsonify
from flask_login import login_required, fresh_login_required
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from flask import session
from app import bcrypt, db
from app.main.forms import LoginForm, RegisterForm, SendResetPasswordRequestForm, ResetPasswordForm
from app.main.email import send_password_reset_email
from app.main.model import User
from . import main
from app import socketio
from app.main.chat_events import users
from app.main.camera import VideoStreamWidget
import cv2
import json
import time
import jsonpickle

cam = None
current_username = ""

@main.route('/')   
@main.route('/index')
@login_required
def index():
    logout_user()
    return render_template('index.html')

@main.route('/home')
def home():
    return render_template('index.html')

                      
@main.route('/login', methods=['GET', 'POST'])
def login():
    """Function for handling requests to the localhost:5000/login endpoint
    """
    form = LoginForm(request.form)
    if form.validate_on_submit():
        global current_username
        username = form.username.data
        current_username = username
        session['user'] = username
        session['active_chat'] = 'group'
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(username=username).first()
        if bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            # return redirect(url_for('main.chat'))
            return render_template('chat.html')
        else:
            flash('Password incorrect', category='danger')
    
    return render_template('login.html',form = form)



@main.route('/chat')
def chat():
    """Function for handling requests to the localhost:5000/chat endpoint
    """
    return render_template('chat.html',users = users)

@main.route('/logout')
def logout():
    """Function for handling requests to the localhost:5000/logout endpoint
    """
    logout_user()
    flash('You have logged out now.', category='info')
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET','POST'])
def register():
    """Function for handling requests to the localhost:5000/register endpoint
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data)
        email = form.email.data
        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, register success. You can log in now.', category='info')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


@main.route('/send_reset_password_request', methods=['GET', 'POST'])
def send_reset_password_request():
    """Function for handling requests to the localhost:5000/send_reset_password endpoint
    """

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SendResetPasswordRequestForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('main.login'))
    return render_template('send_reset_password_request.html', form=form)


@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm(request.form)
    if form.validate_on_submit():
        user = User.verify_reset_password_token(token)
        user.password = bcrypt.generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form)



# @main.route('/video_feed')
# def video_feed():
#     """Video streaming route. Put this in the src attribute of an img tag."""

#     global cam
#     if(cam is None):
#         cam = VideoStreamWidget()
    
    # return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


