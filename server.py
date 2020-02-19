from app import create_app, db,socketio
from flask import session
import cv2
import time
from threading import Thread
from app.main.camera import VideoStreamWidget

app = create_app()


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    print("calling main")   
    socketio.run(app,debug=True)
    app.run(debug=True,threaded=True)         