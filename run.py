from app import app, db

if __name__ == "__main__":
    app.config.from_object('config.DebugConfiguration')
    db.create_all(app=app)
    app.run()
