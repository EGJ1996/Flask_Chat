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
# from server import cam

cam = None
current_username = ""
frames_array = []

@main.route('/')   
# @main.route('/index',methods=['GET','POST'])
@main.route('/index')
@login_required
def index():
    logout_user()
    print("Inside index")
    return render_template('index.html')



                      
@main.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     print("current user is authenticated")
    #     return redirect(url_for('main.index'))
    
    
    form = LoginForm(request.form)
    if form.validate_on_submit():
        print("form validated")
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
    
    print('Routing to chat template, users = '+str(users))
    return render_template('chat.html',users = users)

@main.route('/logout')
def logout():
    logout_user()
    flash('You have logged out now.', category='info')
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET','POST'])
def register():
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

@socketio.on('connected')
def connected(data):
    # cam = VideoStreamWidget()
    print('connected invoked in routes.py file')
    socketio.emit('update_video',{'video_arr':frames_array})

def gen_frame():
    """Video streaming generator function."""
    print('before while loop')
    print('cam = '+str(cam))
    while cam:
        print('inside while loop of gen_frame')
        frame = cam.read()
        print('frame in routes = '+str(frame))
        convert = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n') # concate frame one by one and show result

        time.sleep(0.01)

        frames_array.append({'frame':convert,'user':current_username})
        socketio.emit('video_frame',{'frame':convert,'user':current_username})



@main.route('/video_feed')
def video_feed():
    print('Inside video feed')
    global cam
    if(cam is None):
        cam = VideoStreamWidget()
    
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    # socketio.emit('video_frame',{'resp':resp})
    # return resp


