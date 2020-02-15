from flask import Flask, redirect, session, request,copy_current_request_context,url_for
from flask_socketio import  emit, join_room, leave_room,close_room, rooms, disconnect
from app import socketio
from app.main.camera import VideoStreamWidget
from aylienapiclient import textapi # Sentiment Analysis API
from threading import Lock
import cv2

client = textapi.Client("0f213eed", "9202426a61973183055e9041d1333a07")

users = []
user_presence = {}
all_rooms = []
all_chats = {}

thread = None
thread_lock = Lock()

all_chats['group'] = []
all_rooms.append('group')




def index():
    return redirect(url_for('main.index'))

@socketio.on('joined')
def joined(data):
    """Event handler when the user clicks the join function
    Updates the user list
    """
    user_name = data['user'][5:]
    if(user_name not in list(user_presence.keys())):
        users.append(user_name)
        user_presence[user_name] = True    
    emit("update_users",{'users':users},room=session['room'])

@socketio.on('connected')
def connected(data):
    """Event handler invoked when the socket is connected, i.e., new user joins the chat

    Join_room function is called which puts the user in a room, under the current namespace.
    The namespace is derived from the context
    """
    session['room'] = 'group'
    join_room(session['room'])
    emit("update_users",{'users':users})
    emit('update_messages',{'messages':all_chats['group']})

@socketio.on('add_message')
def add_message(data):
    """Event handler for adding new message

    Invoked when the user clicks the send button in the UI.
    Two cases are considered: 1. message is posted in the public group,
    and in this case all the users that have joined the chat update their message list
    2. Private message, where only the destination user updates its message list
    """
    print('add_message invoked with '+str(data))
    sentiment = client.Sentiment({'text': data['message']})
    print('tone analyzer = ' + sentiment['polarity'])

    if(data['destination'] == 'group'):
        # Case 1: We are writing to the public group
        all_chats['group'].append({'message':data['message'],'origin':data['origin'],'sentiment':sentiment['polarity']})
        emit('update_messages',{'messages':all_chats['group']},room='group')
    
    else:
        # Case 2: 
        all_chats[session['room']].append({'message':data['message'],'origin':data['origin'],'sentiment':sentiment['polarity']})
        print('room = '+session['room'])
        emit('update_messages',{'messages':all_chats[session['room']]},room=session['room'])

@socketio.on('update_chat')
def update_chat(data):
    """Updates the origin and the destination of the message

    When a user click on the username of another user, this 
    event is invoked to update the origin and the destination of the message
    """
    if(session['user'] != data['origin']):
        return
    
    if(data['destination'] == 'group'):
        session['room'] = 'group'
    
    else:    
        tmp_arr = [data['origin'],data['destination']]
        tmp_arr.sort()
        new_room = ''.join(tmp_arr)
        print('Changing the room to ' + new_room)

        if(new_room != session['room']):
            session['room'] = new_room
            join_room(new_room)
        
        if(session['room'] not in all_rooms):
            all_chats[session['room']] = []
            all_rooms.append(session['room'])

    emit('update_messages',{'messages':all_chats[session['room']]},room=session['room'])