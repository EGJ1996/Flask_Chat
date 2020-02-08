from app import create_app, db,socketio
app = create_app()
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    print("calling main")
    socketio.run(app)
    app.run(debug=True)         