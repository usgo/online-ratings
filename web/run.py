from app import get_app

app = get_app('config.DockerConfiguration')
if __name__ == "__main__":
    app.run(host='0.0.0.0')
