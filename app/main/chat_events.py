from flask import Flask, redirect, session, request,copy_current_request_context,url_for
from flask_socketio import  emit, join_room, leave_room,close_room, rooms, disconnect
from app import socketio

users = []
user_presence = {}
all_rooms = []
all_chats = {}

# Only 1 channel implemented currently. Different channels may be implemented by having different rooms


all_chats['group'] = []
all_rooms.append('group')

def index():
    return redirect(url_for('main.index'))

@socketio.on('joined')
def joined(data):
    # print("data keys = "+str(data.keys()))
    user_name = data['user'][5:]
    print("join event called from chat_events with user = "+str(data))

    print('current_user = '+session['user']+" username = "+user_name)
    if(user_name not in list(user_presence.keys())):
        users.append(user_name)
        user_presence[user_name] = True    
    print("length of users = "+str(len(users)))

    # join_room(room)
    emit("update_users",{'users':users},room=session['room'])

@socketio.on('connected')
def connected(data):
    session['room'] = 'group'
    print('called connected with room = '+session['room'])
    join_room(session['room'])
    emit("update_users",{'users':users})
    emit('update_messages',{'messages':all_chats['group']})

@socketio.on('add_message')
def add_message(data):
    
    print('add_message invoked with '+str(data))
    
    if(data['destination'] == 'group'):
        # Case 1: We are writing to the public group
        all_chats['group'].append({'message':data['message'],'origin':data['origin']})
        emit('update_messages',{'messages':all_chats['group']},room='group')
    
    else:
        # Case 2: 
        all_chats[session['room']].append({'message':data['message'],'origin':data['origin']})
        print('room = '+session['room'])
        emit('update_messages',{'messages':all_chats[session['room']]},room=session['room'])

@socketio.on('update_chat')
def update_chat(data):

    if(session['user'] != data['origin']):
        return
    
    if(data['destination'] == 'group'):
        session['room'] = 'group'
    
    else:    
        tmp_arr = [data['origin'],data['destination']]
        tmp_arr.sort()
        new_room = ''.join(tmp_arr)
        print('Changing the room to ' + new_room)

        # join the new room
        if(new_room != session['room']):
            print('joining room')
            # print('leaving room')
            session['room'] = new_room
            # leave_room(room)
            join_room(new_room)
        
        if(session['room'] not in all_rooms):
            all_chats[session['room']] = []
            all_rooms.append(session['room'])
    
    print('room = '+session['room'])
    print('chats of room = ')
    print(all_chats[session['room']])
    emit('update_messages',{'messages':all_chats[session['room']]},room=session['room'])
    # emit('update_messages',{'messages':all_chats[new_room]},room=room)

    

@socketio.on('connect')
def connect():
    print('caught the connect event')


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
