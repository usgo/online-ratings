from app import app

if __name__ == "__main__":
    app.config.from_object('config.DebugConfiguration')
    #db.create_all(app=app)
    app.run(host='0.0.0.0') # TODO: ask daniel.
