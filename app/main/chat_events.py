from flask import Flask, redirect, session, request,copy_current_request_context,url_for
from flask_socketio import  emit, join_room, leave_room,close_room, rooms, disconnect
from app import socketio

users = []
user_presence = {}
all_chats = {}

# Only 1 channel implemented currently. Different channels may be implemented by having different rooms

room = "room1"

def index():
    return redirect(url_for('main.index'))

@socketio.on('joined')
def joined(data):
    print("join event called from chat_events")
    # print("data keys = "+str(data.keys()))
    user_name = data['user'][5:]

    if(user_name not in list(user_presence.keys())):
        users.append(user_name)
        user_presence[user_name] = True
    print("length of users = "+str(len(users)))

    emit("display_users",{'users':users})



@socketio.on('connect')
def connect():
    print('caught the connect event')

@socketio.on('send_message')
def add_message(data):
    if(all_chats[data["user"]] is None):
        all_chats[data["user"]] = []
        all_chats[data["user"]].append(data["message"])


@socketio.on('my_event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()


@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)
