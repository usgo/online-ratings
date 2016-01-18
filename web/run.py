from app import app

if __name__ == "__main__":
    app.config.from_object('config.DockerConfiguration')
    app.run(host='0.0.0.0')
